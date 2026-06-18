import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import random  # 🛡️ تم تأمين الاستيراد لمنع أخطاء الـ NameError أثناء سحب عينات البافر
from database import log_event

# =========================================================================
# 1. محرك البرمجة الوراثية المستقلة المطور (Smart Genetic Programming Engine)
# =========================================================================
class AutonomousFormulaGenerator:
    """
    محرك مطور ومحقن بميزات الفهم التراكمي وسياق الأسواق (Market Regimes).
    يقوم باختراع وخلط صيغ رياضية تربط عوائد الأصول بالمؤشرات الذكية المبتكرة.
    """
    def __init__(self, available_columns=None):
        """
        يتم حقنه بأعمدة المصفوفة الحية ديناميكياً لكسر قيود التسمية الصلبة القديمة.
        """
        # في حال لم تمرر الأعمدة (حالة افتراضية آمنة)، نعتمد الهيكل السداسي المستقر
        if available_columns is None:
            available_columns = [
                'GOLD_Close', 'BTC_Close', 'ETH_Close', 'OIL_Close', 'DXY_Close', 'BONDS_Close',
                'GOLD_Return', 'BTC_Return', 'ETH_Return', 'OIL_Return', 'DXY_Return', 'BONDS_Return',
                'GOLD_RSI', 'GOLD_ATR', 'GOLD_MACD', 'BTC_RSI', 'BTC_ATR', 'BTC_MACD', 'DXY_MA_24'
            ]
            
        # 🧠 فرز ديناميكي فوري للأعمدة الحية المتوفرة في الماتريكس لمنع الـ KeyError نهائياً
        self.assets_closes = [col for col in available_columns if col.endswith('_Close')]
        self.assets_returns = [col for col in available_columns if col.endswith('_Return')]
        
        # ميزات السياق والماكرو المتوفرة حياً
        context_keywords = ['_RSI', '_ATR', '_MACD', '_MA_', 'macro_', 'book_']
        self.context_features = [
            col for col in available_columns 
            if any(key in col for key in context_keywords) and not col.endswith('_Return')
        ]
        
        # صمام أمان: إذا خلت مصفوفة العوائد أو المؤشرات الحية لأي سبب، نؤمنها لتفادي توقف الراندوم
        if not self.assets_returns:
            self.assets_returns = ['GOLD_Return', 'BTC_Return']
        if not self.context_features:
            self.context_features = self.assets_returns

        # مصفوفة العمليات الحسابية والرياضية المدعومة في المعمل الكمي
        self.operators = ['+', '-', '*', '/', 'rolling_mean', 'rolling_std']

    def generate_dynamic_indicator(self):
        """
        يخترع تركيبة جينية رياضية عشوائية ومحكومة بذكاء لربط متغيرين ماليين
        """
        op = random.choice(self.operators)
        
        # دمج آمن لجميع ميزات الإدخال المتاحة في السوق حالياً
        all_pool = self.assets_returns + self.context_features
        
        # اختيار المتغيرات بناءً على نوع العملية الحسابية
        if op in ['rolling_mean', 'rolling_std']:
            var_a = random.choice(all_pool)
            var_b = var_a  # غير مستخدم في العمليات الأحادية
        else:
            var_a = random.choice(all_pool)
            var_b = random.choice(all_pool)
            
        period = random.randint(5, 60)
        rr_target = random.choice([2.0, 3.0, 4.0])  # ضبط جينات إدارة المخاطر الكونية
        
        # توليد سقف عتبة الدخول (Threshold) بناءً على طبيعة المتغير المختار ديناميكياً
        if "Return" in var_a:
            threshold = random.uniform(-0.005, 0.005)
        elif "RSI" in var_a:
            threshold = random.uniform(30.0, 70.0)
        elif "ATR" in var_a:
            threshold = random.uniform(0.5, 5.0)
        else:
            threshold = random.uniform(-2.0, 2.0)
           
        return {
            "operator": op,
            "variable_a": var_a,
            "variable_b": var_b,
            "period": period,
            "threshold": round(threshold, 6),
            "rr_target": rr_target
        }

    def serialize_formula_to_string(self, f):
        """
        يحول البنية القاموسية للاستراتيجية الجينية إلى سلسلة نصية رياضية نقية 
        ليتم حفظها وفحصها عبر الـ Backtest الممتد.
        """
        op = f['operator']
        if op == 'rolling_mean':
            return f"rolling_mean({f['variable_a']}, period={f['period']}) > {f['threshold']}"
        elif op == 'rolling_std':
            return f"rolling_std({f['variable_a']}, period={f['period']}) > {f['threshold']}"
        elif op in ['+', '-', '*', '/']:
            # اختيار عشوائي ذكي لاتجاه الإشارة لجعل الفحص شامل للاختراقات العلوية والسفلية
            direction = ">" if random.random() > 0.5 else "<"
            return f"({f['variable_a']} {op} {f['variable_b']}) {direction} {f['threshold']}"
        else:
            return f"{f['variable_a']} > {f['threshold']}"

# =========================================================================
# 2. الهيكل العصباني لشبكة الـ Deep Q-Network (The Brain Architecture)
# =========================================================================
class QuantumBrainNetwork(nn.Module):
    """
    شبكة عصبية عميقة متعددة الطبقات مصممة لمعالجة مصفوفات البيانات الرياضية عابرة الأسواق
    وتقدير القيم الاحتمالية والـ Q-Values لقرارات التداول الرياضية الصافية.
    """
    def __init__(self, input_dim, output_dim=3):
        super(QuantumBrainNetwork, self).__init__()
        
        # بناء طبقات الإدخال والمعالجة بمرونة ديناميكية تتكيف مع حجم مصفوفة البيانات الكونية
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.1),  # حماية مدمجة ضد فرط التخصيص الحركي (Overfitting)
            
            nn.Linear(256, 128),
            nn.LeakyReLU(0.1),
            
            nn.Linear(128, 64),
            nn.LeakyReLU(0.1),
            
            nn.Linear(64, output_dim)
        )
        
    def forward(self, x):
        return self.network(x)

# =========================================================================
# 3. العميل المستقل ومحرك التعلم اللحظي العميق (True Deep Q-Agent)
# =========================================================================
class TrueDeepQAgent:
    """
    العميل المستقل المسؤول عن إدارة الذاكرة العشوائية المحدثة (Experience Replay Buffer)
    وتنفيذ عمليات التحسين اللحظي المستمر لأوزان الشبكة العصبية بناءً على عوائد الحركة الصافية.
    """
    def __init__(self, input_dim, output_dim=3, lr=0.0005, gamma=0.95):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.gamma = gamma
        
        # تأسيس العقل الفعال وعقل المقارنة المستهدف لضمان استقرار المعادلات الرياضية
        self.brain = QuantumBrainNetwork(input_dim, output_dim)
        self.target_brain = QuantumBrainNetwork(input_dim, output_dim)
        self.update_target_network()
        
        self.optimizer = optim.Adam(self.brain.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        
        # ذاكرة تخزين الخبرات والحركات الرياضية (Replay Memory Buffer)
        self.memory_buffer = []
        self.max_buffer_size = 50000
        self.batch_size = 64
        self.gamma_discount = 0.97  # زيادة النظرة المستقبلية لصفقات الشراء المستمرة
        
        # ======= 🧠 أرقام التحكم في ذكاء العميل الشرائي =======
        self.epsilon = 1.0          # البداية استكشافية كاملة
        self.epsilon_decay = 0.990  # هبوط أسرع للعشوائية (0.990 يجعل الروبوت يعتمد على عقله أسرع بكثير)
        self.epsilon_min = 0.02     # حد أدنى ضئيل جداً للعشوائية لتثبيت دقة التنبؤ خارج العينة
        # ====================================================

    def update_target_network(self):
        """مزامنة الأوزان المستقرة بين شبكة التوقع والشبكة المستهدفة"""
        self.target_brain.load_state_dict(self.brain.state_dict())

    def store_experience(self, state, action, reward, next_state):
        """حفظ الحركة والنتيجة الرياضية في البافر لكسر الارتباطات الزمنية الضارة بالتدريب"""
        if len(self.memory_buffer) >= self.max_buffer_size:
            self.memory_buffer.pop(0)
        self.memory_buffer.append((state, action, reward, next_state))

    def learn_from_buffer(self):
        """
        يسحب عينات عشوائية مكثفة من بافر الذاكرة لإجراء تعديل أمامي وخلفي لأوزان الشبكة العصبية
        """
        if len(self.memory_buffer) < self.batch_size:
            return 0.0
            
        mini_batch = random.sample(self.memory_buffer, self.batch_size)
        
        states = torch.stack([x[0] for x in mini_batch])
        actions = torch.tensor([x[1] for x in mini_batch], dtype=torch.long).unsqueeze(1)
        rewards = torch.tensor([x[2] for x in mini_batch], dtype=torch.float32).unsqueeze(1)
        next_states = torch.stack([x[3] for x in mini_batch])
        
        # حساب قيم الـ Q الحالية والمتوقعة هندسياً بالمعادلات الرياضية الصافية
        current_q = self.brain(states).gather(1, actions)
        
        with torch.no_grad():
            max_next_q = self.target_brain(next_states).max(1)[0].unsqueeze(1)
            target_q = rewards + (self.gamma * max_next_q)
            
        loss = self.criterion(current_q, target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        
        # 🛡️ قص متجهات الانحدار (Gradient Clipping) لمنع الانفجار الرياضي للأوزان
        nn.utils.clip_grad_norm_(self.brain.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        return loss.item()

    def save_weights(self, file_path='quantum_brain_weights.pt'):
        """حفظ أوزان الشبكة العصبية المحدثة لمنع خسارة الذاكرة عند الإيقاف أو إعادة التشغيل"""
        try:
            torch.save(self.brain.state_dict(), file_path)
        except Exception as e:
            log_event("BRAIN_SAVE_ERROR", f"فشل حفظ ملف أوزان الشبكة العصبية المحدثة: {e}")

    def load_weights(self, file_path='quantum_brain_weights.pt'):
        """استدعاء الذاكرة العميقة والأوزان للبدء في الابتكار والتدريب فوراً بشكل مستقر"""
        try:
            import os
            if os.path.exists(file_path):
                # تحميل آمن متوافق مع كرت الشاشة أو المعالج المتوفر بجهازك بدون تعارض أبعاد
                state_dict = torch.load(file_path, map_location=torch.device('cpu'))
                
                # فحص مطابقة الأبعاد بين الملف المخزن وحجم مصفوفة الميزات الحالي لمنع انهيار البرنامج
                stored_dim = state_dict['network.0.weight'].shape[1]
                if stored_dim == self.input_dim:
                    self.brain.load_state_dict(state_dict)
                    self.update_target_network()
                    print("🧠 [Brain Memory] تم استدعاء وتحميل أوزان الذاكرة العميقة بنجاح واستقرار تام.")
                else:
                    print(f"⚠️ [Brain Notice] أبعاد الأوزان المحفوظة ({stored_dim}) تختلف عن أبعاد المصفوفة الحالية ({self.input_dim})؛ سيتم بدء أوزان جديدة متوافقة.")
        except Exception as e:
            print(f"⚠️ تنبيه أثناء تحميل أوزان العقل: {e}")