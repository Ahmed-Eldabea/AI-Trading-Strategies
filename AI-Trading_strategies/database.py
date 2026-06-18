import sqlite3
import json
import os
from datetime import datetime
import pandas as pd

DB_NAME = 'universal_quant_laboratory.db'

def init_universal_database():
    """
    تهيئ قاعدة البيانات وتنشئ الجداول بهيكلية صارمة تضمن عدم تكرار البيانات 
    وتحمي الاستراتيجيات النخبوية الصامدة خارج العينة والمحمية رباعياً من الضياع.
    """
    with sqlite3.connect(DB_NAME) as conn:
        # 1. جدول الاستراتيجيات المستقلة والمؤشرات المخترعة (المطور بدعم قنوات الهيكل الرباعي)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_asset TEXT NOT NULL,
                mathematical_formula TEXT NOT NULL,
                win_rate REAL NOT NULL,
                in_sample_profit REAL NOT NULL,
                out_of_sample_profit REAL NOT NULL,
                out_of_sample_max_dd REAL NOT NULL,
                profit_factor REAL NOT NULL,
                fitness_score REAL NOT NULL,
                generation_origin INTEGER NOT NULL,
                status TEXT NOT NULL,
                
                -- 🛡️ حقن أعمدة الفلاتر والطبقات الذكية الجديدة للحفظ والتحليل الرقمي
                macro_sentiment REAL DEFAULT 0,       
                book_imbalance REAL DEFAULT 0.5,     
                execution_speed_ms REAL DEFAULT 0
            )
        ''')
        
        # 2. جدول سجل العمليات الكونية الشامل (لوج النظام)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS laboratory_system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        
        conn.commit()

def save_autonomous_strategy(target_asset, formula_str, combined_reports, generation, macro_sent=0.0, book_imb=0.5, exec_speed=0.0):
    """
    يحلل التقارير المزدوجة (الداخلية والخارجية) بناءً على مقياس الأرباح المركبة الجديد،
    ويفرز الصيغ جينياً إما كـ ELITE مستقرة أو REJECTED عشوائية، ثم يحفظها فوراً في الذاكرة الحديدية.
    """
    is_report = combined_reports.get("in_sample", {})
    oos_report = combined_reports.get("out_of_sample", {})
    
    in_sample_profit = float(is_report.get("net_profit_pct", -100.0))
    out_of_sample_profit = float(oos_report.get("net_profit_pct", -100.0))
    out_of_sample_max_dd = float(oos_report.get("max_drawdown", 100.0))
    win_rate = float(oos_report.get("win_rate", 0.0))
    profit_factor = float(oos_report.get("profit_factor", 0.0))
    fitness_score = float(oos_report.get("fitness_score", -1.0))
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 🧠 الفلتر الجيني الصارم والمطور خصيصاً للأرباح المركبة:
    # نقبل الاستراتيجية كنخبة فقط إذا كانت أرباحها إيجابية وتراجعها محكوم تماماً تحت الـ 12%
    if out_of_sample_profit > 15.0 and out_of_sample_max_dd < 12.0 and win_rate > 55.0:
        status = "ELITE"
    else:
        status = "REJECTED"
        
    query = '''
        INSERT INTO autonomous_strategies (
            timestamp, target_asset, mathematical_formula, win_rate, 
            in_sample_profit, out_of_sample_profit, out_of_sample_max_dd, 
            profit_factor, fitness_score, generation_origin, status,
            macro_sentiment, book_imbalance, execution_speed_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(query, (
            timestamp, target_asset, formula_str, win_rate,
            in_sample_profit, out_of_sample_profit, out_of_sample_max_dd,
            profit_factor, fitness_score, generation, status,
            macro_sent, book_imb, exec_speed
        ))
        conn.commit()

def get_latest_generation():
    """
    يستعلم عن آخر جيل مسجل في قاعدة البيانات لضمان استمرارية التعلم التراكمي للـ DQN عند إعادة التشغيل.
    """
    query = "SELECT MAX(generation_origin) FROM autonomous_strategies"
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row and row[0] is not None:
            return int(row[0])
    return 0

def log_event(event_type, description):
    """
    يسجل الأحداث الجوهرية وحالات الإيقاف الآمن في جدول لوج المختبر لضمان سلامة الهيكل الثنائي.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = "INSERT INTO laboratory_system_logs (timestamp, event_type, description) VALUES (?, ?, ?)"
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(query, (timestamp, event_type, description))
        conn.commit()

def scan_cognitive_memory(min_profit=15.0, max_dd=12.0, asset=None, sentiment=None):
    """
    تمشيط ذكي للذاكرة المعرفية للبحث عن الصيغ النخبوية بناءً على معايير الأداء المركب المحدثة.
    """
    query = "SELECT * FROM autonomous_strategies WHERE out_of_sample_profit >= ? AND out_of_sample_max_dd <= ?"
    params = [min_profit, max_dd]
    
    if asset is not None:
        query += " AND target_asset = ?"
        params.append(asset.upper())
    if sentiment is not None:
        query += " AND macro_sentiment = ?"
        params.append(sentiment)
        
    query += " ORDER BY fitness_score DESC"
    
    with sqlite3.connect(DB_NAME) as conn:
        df_results = pd.read_sql_query(query, conn, params=params)
        
    print(f"\n🔎 === نتائج تمشيط الذاكرة المعرفية المحدثة (تم العثور على {len(df_results)} صيغة مبتكرة وثابتة) ===")
    print("=" * 115)
    
    if not df_results.empty:
        for idx, row in df_results.iterrows():
            print(f"📌 كود الصيغة: {row['id']} | الأصل المستهدف: {row['target_asset']} | الوضع الحالي: [{row['status']}]")
            print(f"🏋️ أرباح التدريب (In-Sample): {row['in_sample_profit']:.2f}%")
            print(f"🔮 أرباح الاختبار الأعمى (Out-of-Sample): {row['out_of_sample_profit']:.2f}% | 📉 أقصى تراجع أعمى (OOS Max DD): {row['out_of_sample_max_dd']:.2f}%")
            print(f"🎯 معدل النجاح: {row['win_rate']}% | ⚖️ معامل الربحية (Profit Factor): {row['profit_factor']}\"")
            print(f"🧠 بيئة الصيغة الرياضية: {row['mathematical_formula']}")
            print("-" * 115)
    else:
        print("⚠️ لم يتم العثور على صيغ تطابق هذه الشروط الصارمة في الأجيال الحالية.")