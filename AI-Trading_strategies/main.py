import numpy as np
import pandas as pd
import time
import json
from datetime import datetime
import sqlite3
import warnings
import random 
import os
warnings.filterwarnings("ignore", category=RuntimeWarning)

# استيراد الطبقات والدوال من ملفات مشروعك
from database import init_universal_database, save_autonomous_strategy, get_latest_generation, log_event
from data_ingestion import build_global_market_matrix
from brain_models import AutonomousFormulaGenerator, TrueDeepQAgent, torch

# =========================================================================
# 1. محرك الفحص التاريخي الحقيقي ثنائي الاتجاه (Bi-Directional Swing Evaluator)
# =========================================================================
def execute_rigorous_backtest(df, formula, target_asset="BTC"):
    try:
        op = formula['operator']
        var_a_name = formula['variable_a']
        var_b_name = formula['variable_b']
        
        if "Return" in var_a_name or "Return" in var_b_name:
            if op in ['/', '*', '+', '-']:
                return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 0.0, "profit_factor": 0, "fitness_score": -1}

        if var_a_name not in df.columns or var_b_name not in df.columns:
            return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 0.0, "profit_factor": 0, "fitness_score": -1}

        # تأمين مرن لأسماء الأعمدة (كابيتال أو سمول)
        open_col = f'{target_asset}_Open' if f'{target_asset}_Open' in df.columns else (f'{target_asset}_open' if f'{target_asset}_open' in df.columns else None)
        high_col = f'{target_asset}_High' if f'{target_asset}_High' in df.columns else (f'{target_asset}_high' if f'{target_asset}_high' in df.columns else None)
        low_col = f'{target_asset}_Low' if f'{target_asset}_Low' in df.columns else (f'{target_asset}_low' if f'{target_asset}_low' in df.columns else None)
        close_col = f'{target_asset}_Close' if f'{target_asset}_Close' in df.columns else (f'{target_asset}_close' if f'{target_asset}_close' in df.columns else None)

        if not all([open_col, high_col, low_col, close_col]):
            return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 0.0, "profit_factor": 0, "fitness_score": -1}

        var_a = df[var_a_name].values
        var_b = df[var_b_name].values
        period = formula['period']
        
        if op == '+': signal_line = var_a + var_b
        elif op == '-': signal_line = var_a - var_b
        elif op == '*': signal_line = var_a * var_b
        elif op == '/': signal_line = var_a / (var_b + 1e-10)
        elif op == 'rolling_mean': signal_line = pd.Series(var_a).rolling(period, min_periods=max(2, period)).mean().values
        elif op == 'rolling_std': signal_line = pd.Series(var_a).rolling(period, min_periods=max(2, period)).std().values
        else: signal_line = var_a
        
        signal_line = np.nan_to_num(signal_line, nan=0.0)
        
        open_prices = df[open_col].values
        high_prices = df[high_col].values
        low_prices = df[low_col].values
        close_prices = df[close_col].values
        
        # إعداد الحساب نظيف ومستقل لكل فحص لمنع تراكم التصفير
        initial_balance = 10000.0
        balance = initial_balance
        peak = balance
        max_dd = 0.0
        wins, losses = 0, 0
        
        trading_fee = 0.0004  # عمولة سوق حقيقية متوازنة لحسابات الفئة الاحترافية
        risk_pct = 0.01        # مخاطرة ثابتة 1% من الحساب لكل صفقة لحمايته من الموت
        stop_distance_pct = 0.035  # نطاق حركة حماية عريض 3.5% يناسب تذبذب BTC العنيف
        rr_target = formula.get('rr_target', 3.0)
        
        in_trade = False
        trade_type = None  # يمكن أن يكون 'LONG' أو 'SHORT'
        entry_price = 0.0
        stop_loss_price = 0.0
        take_profit_price = 0.0
        
        # سحب نوع الاختراق من التركيبة الجينية
        condition_direction = formula.get('condition_type', '>') 
        
        start_idx = max(100, period)
        if start_idx >= len(df):
            return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 0.0, "profit_factor": 0, "fitness_score": -1}

        for i in range(start_idx, len(df)):
            high_p = high_prices[i]
            low_p = low_prices[i]
            open_p = open_prices[i]
            close_p = close_prices[i]
            
            # -----------------------------------------------------------------
            # أولاً: إدارة الصفقة النشطة (تتبع المنطق ثنائي الاتجاه بشكل صارم)
            # -----------------------------------------------------------------
            if in_trade:
                if trade_type == 'LONG':
                    # فحص ضرب الوقف أولاً كحماية صارمة (Conservative Approach)
                    if low_p <= stop_loss_price:
                        trade_pnl = -(initial_balance * risk_pct) - (balance * trading_fee)
                        balance += trade_pnl
                        losses += 1
                        in_trade = False
                    elif high_p >= take_profit_price:
                        trade_pnl = ((initial_balance * risk_pct) * rr_target) - (balance * trading_fee)
                        balance += trade_pnl
                        wins += 1
                        in_trade = False
                        
                elif trade_type == 'SHORT':
                    # في صفقة البيع المكشوف: الستوب يكون لأعلى والتارجت لأسفل
                    if high_p >= stop_loss_price:
                        trade_pnl = -(initial_balance * risk_pct) - (balance * trading_fee)
                        balance += trade_pnl
                        losses += 1
                        in_trade = False
                    elif low_p <= take_profit_price:
                        trade_pnl = ((initial_balance * risk_pct) * rr_target) - (balance * trading_fee)
                        balance += trade_pnl
                        wins += 1
                        in_trade = False
            
            # -----------------------------------------------------------------
            # ثانياً: فحص شروط الدخول الجينية الثنائية (Long & Short)
            # -----------------------------------------------------------------
            else:
                if signal_line[i] == 0.0 or signal_line[i-1] == 0.0:
                    continue
                    
                is_long_triggered = False
                is_short_triggered = False
                
                # إذا كان اتجاه الشرط جينياً هو ">"
                if condition_direction == '>':
                    # اختراق لأعلى -> إشارة شراء LONG
                    if signal_line[i] > formula['threshold'] and signal_line[i-1] <= formula['threshold']:
                        is_long_triggered = True
                    # كسر لأسفل -> إشارة بيع SHORT
                    elif signal_line[i] < -formula['threshold'] and signal_line[i-1] >= -formula['threshold']:
                        is_short_triggered = True
                else:
                    # إذا كان اتجاه الشرط هو "<"
                    if signal_line[i] < formula['threshold'] and signal_line[i-1] >= formula['threshold']:
                        is_long_triggered = True
                    elif signal_line[i] > -formula['threshold'] and signal_line[i-1] <= -formula['threshold']:
                        is_short_triggered = True

                # تنفيذ صفقات الشراء
                if is_long_triggered:
                    in_trade = True
                    trade_type = 'LONG'
                    entry_price = open_p  
                    stop_loss_price = entry_price * (1 - stop_distance_pct)
                    take_profit_price = entry_price * (1 + (stop_distance_pct * rr_target))
                
                # تنفيذ صفقات البيع المكشوف
                elif is_short_triggered:
                    in_trade = True
                    trade_type = 'SHORT'
                    entry_price = open_p  
                    stop_loss_price = entry_price * (1 + stop_distance_pct) # الستوب أعلى السعر في الـ Short
                    take_profit_price = entry_price * (1 - (stop_distance_pct * rr_target)) # الربح أسفل السعر

            # قياس التراجع الأقصى
            if balance > peak: peak = balance
            dd = (peak - balance) / peak if peak > 0 else 0.0
            if dd > max_dd: max_dd = dd
            
            if balance <= 0:
                balance = 0.0
                break
                
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        net_profit_pct = ((balance - initial_balance) / initial_balance) * 100
        
        if total_trades == 0:
            return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 0.0, "profit_factor": 0, "fitness_score": 0}
            
        profit_factor = (wins * rr_target) / (losses if losses > 0 else 1)
        fitness_score = (net_profit_pct * (win_rate / 100)) / (max_dd + 1e-6)
       
        return {
            "win_rate": round(win_rate, 2), 
            "net_profit_pct": round(net_profit_pct, 2),
            "max_drawdown": round(max_dd * 100, 2), 
            "profit_factor": round(profit_factor, 2),
            "fitness_score": round(fitness_score, 4)
        }
    except Exception as e:
        return {"win_rate": 0, "net_profit_pct": 0.0, "max_drawdown": 100, "profit_factor": 0, "fitness_score": -1}

# =========================================================================
# 2. حلقة تشغيل المختبر الجيني الثاني المستقل (The Gen-2 Eternal Master Loop)
# =========================================================================
def start_master_laboratory_pipeline():
    init_universal_database()
    
    # 🧠 التحقق المطور لملف الأوزان: الاستدعاء والمواصلة بدلاً من الإبادة والتصفير
    weights_file = 'quantum_brain_v2_btc.pt'
    has_pre_trained_weights = False
    
    if os.path.exists(weights_file):
        try:
            has_pre_trained_weights = True
            print("💾 [System Resume] تم العثور على ملف الأوزان السابق. سيتم تحميل العقل الذكي للمواصلة وتطوير الأجيال.")
        except:
            pass
    else:
        print("🧹 [System Reset] لم يتم العثور على أوزان سابقة. سيبدأ النظام من الجيل النظيف رقم #1.")

    generation = 0 
    print(f"🏁 [System Startup] المختبر الجيني الثنائي (Gen-2) نشط للبيتكوين. نقطة الانطلاق: الجيل #1")
    
    market_map = build_global_market_matrix()
    if market_map is None or market_map.empty:
        print("❌ خطأ حرج: مصفوفة البيانات فارغة. تحقق من الاتصال وقاعدة البيانات.")
        return
        
    feature_cols = market_map.select_dtypes(include=[np.number]).columns.tolist()
    
    # بناء العميل الذكي وحصر حجم المدخلات
    ai_agent = TrueDeepQAgent(input_dim=len(feature_cols))
    
    # تحميل الأوزان المخزنة داخل العميل إذا كانت موجودة فعلياً
    if has_pre_trained_weights:
        try:
            if hasattr(ai_agent, 'load_weights'):
                ai_agent.load_weights(weights_file)
            elif hasattr(ai_agent, 'model') and os.path.exists(weights_file):
                ai_agent.model.load_state_dict(torch.load(weights_file))
            print("✅ [Brain Loaded] تم دمج الأوزان التاريخية بنجاح داخل شبكة الـ DQN.")
        except Exception as e:
            print(f"⚠️ [Warning] تعذر دمج ملف الأوزان بسبب اختلاف الهيكلية: {e}. سيتم البدء بأوزان عشوائية آمنة.")
            
    formula_engine = AutonomousFormulaGenerator(available_columns=feature_cols)
    
    print("\n🚀 [Matrix Online] محرك البيتكوين المطور (شراء وبيع محمي) انطلق الآن...")
    print("=" * 115)
    
    try:
        while True:
            market_map = build_global_market_matrix()
            
            if market_map is None or market_map.empty or len(market_map) < 150:
                print("⚠️ [Warning] جاري تجميع مصفوفة البيانات حياً وضمان اكتمال الشموع...")
                time.sleep(4)
                continue
            
            generation += 1
            
            feature_cols = market_map.select_dtypes(include=[np.number]).columns.tolist()
            for col in feature_cols:
                market_map[col] = market_map[col].astype(np.float32)
                
            market_map.index = pd.to_datetime(market_map.index)
            
            # الفرز المستقر للفحص الأعمى (75% في العينة / 25% خارج العينة الصارمة)
            split_idx = int(len(market_map) * 0.75)
            in_sample_df = market_map.iloc[:split_idx]
            out_of_sample_df = market_map.iloc[split_idx:]
            
            if len(in_sample_df) == 0 or len(out_of_sample_df) == 0:
                continue

            # 🧠 تدريب الـ DQN الذاتي وتثبيت العوائد الصافية لحركات الأسعار
            live_fee = 0.0003  
            btc_ret_col = 'BTC_Return' if 'BTC_Return' in market_map.columns else (f'BTC_return' if f'BTC_return' in market_map.columns else feature_cols[0])
            
            for i in range(len(market_map) - 1):
                state = torch.tensor(market_map.iloc[i][feature_cols].values.astype(np.float32), dtype=torch.float32)
                next_state = torch.tensor(market_map.iloc[i+1][feature_cols].values.astype(np.float32), dtype=torch.float32)
                action = random.choice([0, 1, 2])
                
                if action == 1: reward = market_map.iloc[i+1][btc_ret_col] - live_fee
                elif action == 2: reward = -market_map.iloc[i+1][btc_ret_col] - live_fee
                else: reward = 0.0
                
                ai_agent.store_experience(state, action, reward * 100, next_state)
                if i % 20 == 0: 
                    ai_agent.learn_from_buffer()
                    if hasattr(ai_agent, 'epsilon') and ai_agent.epsilon > ai_agent.epsilon_min:
                        ai_agent.epsilon *= ai_agent.epsilon_decay
                    
            ai_agent.update_target_network()
            ai_agent.save_weights(weights_file)
            
            print(f"\n⏳ [Processing] صدم وغربلة 60 صيغة جينية (LONG/SHORT) للجيل الجديد #{generation}...")
            
            latest_macro_sentiment = float(market_map['macro_sentiment'].iloc[-1]) if 'macro_sentiment' in market_map.columns else 0.0
            latest_book_imbalance = float(market_map['book_imbalance'].iloc[-1]) if 'book_imbalance' in market_map.columns else 0.5
       
            target = "BTC"
            for _ in range(60):
                try:
                    formula = formula_engine.generate_dynamic_indicator()
                    
                    formula_str_temp = formula_engine.serialize_formula_to_string(formula)
                    if "<" in formula_str_temp:
                        formula['condition_type'] = '<'
                    else:
                        formula['condition_type'] = '>'

                    start_time = time.time()
                   
                    report_is = execute_rigorous_backtest(in_sample_df, formula, target_asset=target)
                    report_oos = execute_rigorous_backtest(out_of_sample_df, formula, target_asset=target)
                    
                    target_oos_profit = report_oos["net_profit_pct"]
                    target_oos_dd = report_oos["max_drawdown"]
                    target_win_rate = report_oos["win_rate"]

                    # حساب إشارة المكافأة النظيفة للنموذج الجديد
                    if target_oos_dd > 0:
                        reward = (target_oos_profit / (target_oos_dd + 1e-3)) * (target_win_rate / 100.0)
                    else:
                        reward = target_oos_profit * 2.0  

                    if target_oos_profit == 0:
                        reward -= 4.0  
                    elif target_oos_profit < 0:
                        reward -= 2.0  

                    execution_speed_ms = (time.time() - start_time) * 1000
                    formula_str = formula_engine.serialize_formula_to_string(formula)
                    
                    combined_reports = {"in_sample": report_is, "out_of_sample": report_oos}
                    
                    save_autonomous_strategy(
                        target_asset=target, formula_str=formula_str, combined_reports=combined_reports, 
                        generation=generation, macro_sent=latest_macro_sentiment, 
                        book_imb=latest_book_imbalance, exec_speed=execution_speed_ms
                    )
                except:
                    pass
            
            print(f"\n👑 === QUANT LAB MASTER PIPELINE REPORT (GEN-2 BTC #{generation}) ===")
            print(f"⏱️ Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            with sqlite3.connect('universal_quant_laboratory.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT target_asset, in_sample_profit, out_of_sample_profit, out_of_sample_max_dd, 
                           status, mathematical_formula 
                    FROM autonomous_strategies 
                    WHERE generation_origin=? AND target_asset='BTC'
                    ORDER BY out_of_sample_profit DESC LIMIT 5
                """, (generation,))
                rows = cursor.fetchall()
                
                if rows:
                    print(f"\n📊 Live Snapshot from Gen-2 #{generation} (Pure Long & Short Armor):")
                    print(f"{'Asset':<6} | {'IS Prof':<8} | {'OOS Prof':<8} | {'OOS DD':<7} | {'Status':<10} | {'Mathematical Formula'}")
                    print("-" * 115)
                    for r in rows:
                        print(f"{r[0]:<6} | {r[1]:<7}% | {r[2]:<8}% | {r[3]:<6}% | {r[4]:<10} | {r[5]}")
                else:
                    print("\n⏳ Generating formulas and identifying alpha factors via multi-directional rules...")
            print("=" * 115)
            
            time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n🛑 [SHUTDOWN SECURE] تم إيقاف النظام الجيني الجديد بسلام التعديلات.")

if __name__ == "__main__":
    start_master_laboratory_pipeline()