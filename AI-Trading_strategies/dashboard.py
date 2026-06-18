import os
import sqlite3
import pandas as pd

DB_NAME = 'universal_quant_laboratory.db'

def clear_screen():
    """تنظيف الشاشة لجعل الواجهة مريحة وسهلة القراءة"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 115)
    print("  🖥️  نظام الاستعلام المالي الذكي وتصفح ذاكرة الأبحاث الكمية الكونية (تحديث نظام العوائد المركبة)  ")
    print("=" * 115)

def run_dashboard_menu():
    if not os.path.exists(DB_NAME):
        print(f"❌ خطأ: لم يتم العثور على ملف قاعدة البيانات '{DB_NAME}'.")
        print("💡 تأكد من تشغيل ملف المحرك الأساسي (main.py) أولاً لكي يقوم بتأسيس الذاكرة.")
        return

    while True:
        clear_screen()
        print_header()
        print("\n[1] 🔍 استخراج الاستراتيجيات بناءً على قيود الأداء المركب وفلاتر الأداء الصارمة")
        print("[2] 🏆 عرض أفضل 10 استراتيجيات نخبة (ELITE) صامدة في تاريخ عمل المختبر")
        print("[3] ⚠️  استخراج الاستراتيجيات المرفوضة لتحليل أسباب الفشل جينياً")
        print("[4] 📊 عرض ملخص حجم وإحصائيات المعرفة الكلية داخل قاعدة البيانات")
        print("[5] 🚪 خروج من لوحة التحكم")
        print("=" * 115)
        
        choice = input("✍️  برجاء اختيار رقم الأمر المراد تنفيذه (1-5): ")
        
        if choice == '1':
            clear_screen()
            print_header()
            print("\n🔍 ضبط فلاتر الاستعلام الرياضية المركبة:")
            print("-" * 50)
            try:
                min_profit = float(input("🎯 الحد الأدنى لأرباح الاختبار الأعمى المطلوبة المستهدفة (OOS Compounding Profit %): ") or "15.0")
                max_dd = float(input("📉 الحد الأقصى للتراجع الأعمى المسموح به (OOS Max Drawdown %): ") or "12.0")
                
                # 🪙 تحديث وإرشاد المستخدم للأصول الستة الحالية النشطة في العقل والبيانات
                asset_choice = input("🪙 حدد الأصل المستهدف (BTC, ETH, GOLD, DXY, OIL, BONDS أو اضغط Enter للكل): ").strip().upper()
                
                query = """
                    SELECT id, target_asset, in_sample_profit, out_of_sample_profit, 
                           out_of_sample_max_dd, win_rate, profit_factor, generation_origin, status, mathematical_formula 
                    FROM autonomous_strategies 
                    WHERE out_of_sample_profit >= ? AND out_of_sample_max_dd <= ?
                """
                params = [min_profit, max_dd]
                
                if asset_choice:
                    query += " AND target_asset = ?"
                    params.append(asset_choice)
                    
                query += " ORDER BY out_of_sample_profit DESC LIMIT 30"
                
                with sqlite3.connect(DB_NAME) as conn:
                    df = pd.read_sql_query(query, conn, params=params)
                    
                print(f"\n✅ تم العثور على {len(df)} صيغة تطابق شروط الأداء الرياضي الصارم:")
                print("-" * 115)
                if not df.empty:
                    for idx, row in df.iterrows():
                        print(f"📌 كود: {row['id']} | الأصل: {row['target_asset']} | الجيل: #{row['generation_origin']} | الوضع: [{row['status']}]")
                        print(f"🏋️ أرباح التدريب المركبة (IS): {row['in_sample_profit']}% | 🔮 أرباح الاختبار الأعمى المركبة (OOS): {row['out_of_sample_profit']}%")
                        print(f"📉 أقصى تراجع أعمى: {row['out_of_sample_max_dd']}% | 🎯 نسبة النجاح: {row['win_rate']}% | ⚖️ معامل الربحية: {row['profit_factor']}")
                        print(f"🧠 المعادلة الجينية: {row['mathematical_formula']}")
                        print("-" * 115)
                else:
                    print("⚠️ لا توجد صيغ تطابق هذه المعايير المرتفعة في الأجيال الحالية.")
            except Exception as e:
                print(f"❌ حدث خطأ أثناء تصفية البيانات: {str(e)}")
            input("\n🔙 اضغط Enter للعودة إلى القائمة...")

        elif choice == '2':
            clear_screen()
            print_header()
            print("\n🏆 قاعة مشاهير النخبة الرياضية - أفضل 10 استراتيجيات (ELITE) حسب الأرباح المركبة:")
            print("-" * 115)
            
            query = """
                SELECT id, target_asset, in_sample_profit, out_of_sample_profit, 
                       out_of_sample_max_dd, win_rate, profit_factor, generation_origin, mathematical_formula 
                FROM autonomous_strategies 
                WHERE status = 'ELITE' 
                ORDER BY out_of_sample_profit DESC LIMIT 10
            """
            with sqlite3.connect(DB_NAME) as conn:
                df = pd.read_sql_query(query, conn)
                
            if not df.empty:
                for idx, row in df.iterrows():
                    print(f"👑 الترتيب #{idx+1} | كود الصيغة: {row['id']} | الأصل: {row['target_asset']} | جيل: #{row['generation_origin']}")
                    print(f"🔮 العوائد المركبة الصافية خارج العينة (OOS): {row['out_of_sample_profit']}% | 📉 أقصى تراجع: {row['out_of_sample_max_dd']}%")
                    print(f"🎯 دقة الصفقات: {row['win_rate']}% | ⚖️ معامل الربح: {row['profit_factor']} | 🏋️ أرباح التدريب الداخلي: {row['in_sample_profit']}%")
                    print(f"🚀 التركيبة الرياضية: {row['mathematical_formula']}")
                    print("-" * 115)
            else:
                print("⚠️ الذاكرة الحديدية لا تحتوي على استراتيجيات النخبة حتى الآن. دع المفرمة تعمل لعدة أجيال مركبة أولاً.")
            input("\n🔙 اضغط Enter للعودة إلى القائمة...")

        elif choice == '3':
            clear_screen()
            print_header()
            print("\n⚠️  مستودع السجلات المستبعدة (REJECTED) - أعلى 10 صيغ قريبة من حافة القبول للتلقيم العكسي:")
            print("-" * 115)
            
            query = """
                SELECT id, target_asset, in_sample_profit, out_of_sample_profit, 
                       out_of_sample_max_dd, win_rate, generation_origin, mathematical_formula 
                FROM autonomous_strategies 
                WHERE status = 'REJECTED' AND out_of_sample_profit > 0
                ORDER BY out_of_sample_profit DESC LIMIT 10
            """
            with sqlite3.connect(DB_NAME) as conn:
                df = pd.read_sql_query(query, conn)
                
            if not df.empty:
                for idx, row in df.iterrows():
                    print(f"❌ السجل المستبعد | كود: {row['id']} | الأصل: {row['target_asset']} | جيل: #{row['generation_origin']}")
                    print(f"📈 أرباح عشوائية مسجلة: {row['out_of_sample_profit']}% | 🛑 سبب الاستبعاد الأساسي تراجع عنيف: {row['out_of_sample_max_dd']}%")
                    print(f"🎯 نسبة الصفقات: {row['win_rate']}% | 🏋️ أرباح التدريب: {row['in_sample_profit']}%")
                    print(f"🔬 المعادلة المستبعدة: {row['mathematical_formula']}")
                    print("-" * 115)
            else:
                print("⚠️ لا توجد صيغ مرفوضة بأرباح إيجابية حالياً في قاعدة البيانات.")
            input("\n🔙 اضغط Enter للعودة إلى القائمة...")

        elif choice == '4':
            clear_screen()
            print_header()
            print("\n📊 ملخص حجم وقوة المعرفة الكلية المخزنة داخل الذاكرة الحديدية المحدثة:")
            print("-" * 115)
            
            with sqlite3.connect(DB_NAME) as conn:
                total_strategies = conn.execute("SELECT COUNT(*) FROM autonomous_strategies").fetchone()[0]
                elite_count = conn.execute("SELECT COUNT(*) FROM autonomous_strategies WHERE status='ELITE'").fetchone()[0]
                rejected_count = conn.execute("SELECT COUNT(*) FROM autonomous_strategies WHERE status='REJECTED'").fetchone()[0]
                max_generation = conn.execute("SELECT MAX(generation_origin) FROM autonomous_strategies").fetchone()[0]
                
            print(f"🧠 إجمالي المعادلات والمؤشرات المخترعة والمفحوصة كلياً بنظام التراكم: {total_strategies}")
            print(f"🔥 عدد استراتيجيات النخبة الصامدة العابرة للاختبارات (ELITE): {elite_count}")
            print(f"🛑 عدد صيغ التجارب المستبعدة والمرفوضة (REJECTED): {rejected_count}")
            print(f"🧬 إجمالي الأجيال والتحسينات التطورية الكلية للمحرك: #{max_generation if max_generation else 0}")
            print("-" * 115)
            
            input("\n🔙 اضغط Enter للعودة إلى القائمة الرئيسية...")

        elif choice == '5':
            print("\n👋 تم إغلاق لوحة التحكم بنجاح. طاب يومك يا أحمد وطابت أبحاثك الكمية!")
            break
        else:
            input("\n⚠️ اختيار خاطئ! اضغط Enter وحاول مجدداً...")

if __name__ == "__main__":
    run_dashboard_menu()