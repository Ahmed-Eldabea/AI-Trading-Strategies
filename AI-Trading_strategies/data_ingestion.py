import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
from database import log_event

def fetch_asset_in_chunks(ticker, interval="1h"):
    """
    تجلب بيانات الساعة بأعلى مدى مستقر وآمن حركياً لتفادي قيود ياهو فاينانس (715 يوماً)
    """
    try:
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=715)
        
        df = yf.download(
            tickers=ticker, 
            start=start_date.strftime('%Y-%m-%d'), 
            end=end_date.strftime('%Y-%m-%d'), 
            interval=interval, 
            progress=False
        )
        
        # 🛡️ تطهير فوري لمستويات الأعمدة الزائدة لمنع الـ KeyError الصامت تماماً
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if not df.empty and 'Close' in df.columns:
            return df
            
        # خطة طوارئ دفاعية فورية بطلب عمق أقل في حال تشديد خوادم الـ IP
        print(f"⚠️ تنبيه: نافذة الـ 715 يوماً للأصل {ticker} واجهت فجوة اتصال، جاري تفعيل خطة الطوارئ (360 يوماً)...")
        df_short = yf.download(tickers=ticker, period="360d", interval=interval, progress=False)
        if isinstance(df_short.columns, pd.MultiIndex):
            df_short.columns = df_short.columns.get_level_values(0)
        return df_short
        
    except Exception as e:
        log_event("DATA_FETCH_ERROR", f"خطأ أثناء جلب {ticker}: {str(e)}")
        return pd.DataFrame()

def generate_historical_macro_and_liquidity(index_timeline):
    df_macro = pd.DataFrame(index=index_timeline)
    df_macro['macro_sentiment'] = 0.0
    df_macro['book_imbalance'] = 0.5
    return df_macro

def inject_smart_context_features_internal(df, target_asset="GOLD"):
    close_col = f'{target_asset}_Close'
    high_col = f'{target_asset}_High'
    low_col = f'{target_asset}_Low'
    
    if close_col not in df.columns:
        return df
        
    delta = df[close_col].astype(float).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / np.where(loss == 0, 0.000001, loss)
    df[f'{target_asset}_RSI'] = 100 - (100 / (1 + rs))
    
    if high_col in df.columns and low_col in df.columns:
        high_low = df[high_col].astype(float) - df[low_col].astype(float)
        high_close = np.abs(df[high_col].astype(float) - df[close_col].astype(float).shift(1))
        low_close = np.abs(df[low_col].astype(float) - df[close_col].astype(float).shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df[f'{target_asset}_ATR'] = tr.rolling(window=14, min_periods=1).mean()
    else:
        df[f'{target_asset}_ATR'] = 1.0
        
    exp1 = df[close_col].astype(float).ewm(span=12, adjust=False, min_periods=1).mean()
    exp2 = df[close_col].astype(float).ewm(span=26, adjust=False, min_periods=1).mean()
    df[f'{target_asset}_MACD'] = exp1 - exp2
    
    return df

def build_global_market_matrix():
    cache_file = "global_market_matrix_cache.parquet"
    
    # تفحص وجود الكاش الصلب كخيار أول للاستقرار السريع
    if os.path.exists(cache_file):
        try:
            df_cached = pd.read_parquet(cache_file)
            if df_cached is not None and not df_cached.empty and len(df_cached) > 100:
                return df_cached
        except:
            pass

    print("📊 [Data Ingestion] جاري بناء مصفوفة البيانات الرياضية الموحدة للأصول الكبرى...")
    
    market_symbols = {
        'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'GOLD': 'GC=F',
        'DXY': 'DX-Y.NYB', 'OIL': 'CL=F', 'BONDS': '^TYX'
    }
    
    master_matrix = pd.DataFrame()
    
    for asset_name, ticker in market_symbols.items():
        try:
            df_asset = fetch_asset_in_chunks(ticker, interval="1h")
            if not df_asset.empty:
                df_asset.index = pd.to_datetime(df_asset.index)
                
                # استخراج السلسلة السعرية النظيفة مع ضمان الأبعاد الأحادية (1D Series)
                close_s = df_asset['Close'].iloc[:, 0] if len(df_asset['Close'].shape) > 1 else df_asset['Close']
                high_s = df_asset['High'].iloc[:, 0] if len(df_asset['High'].shape) > 1 else df_asset['High']
                low_s = df_asset['Low'].iloc[:, 0] if len(df_asset['Low'].shape) > 1 else df_asset['Low']
                
                df_temp = pd.DataFrame({
                    f'{asset_name}_Close': close_s,
                    f'{asset_name}_High': high_s,
                    f'{asset_name}_Low': low_s
                }, index=df_asset.index)
                
                # الدمج الخارجي المرن لمنع تصفير المصفوفة عند سقوط اتصال أحد الأصول
                if master_matrix.empty:
                    master_matrix = df_temp
                else:
                    master_matrix = master_matrix.join(df_temp, how='outer')
        except Exception as e:
            print(f"⚠️ تنبيه: تعذر دمج أصل {asset_name} حياً حالياً: {e}")
            
    if master_matrix.empty or len(master_matrix) < 50:
        if os.path.exists(cache_file):
            return pd.read_parquet(cache_file)
        return None
        
    try:
        master_matrix.index = pd.to_datetime(master_matrix.index)
        master_matrix.index.name = 'Time'
        
        # ملء الفجوات الحركية الناتجة عن اختلاف أوقات عمل الأسواق (الكريبتو والبورصات التقليدية)
        master_matrix.ffill(inplace=True)
        master_matrix.bfill(inplace=True)
        
        # احتساب المؤشرات الفنية للذهب والبيتكوين بأمان كامل
        master_matrix = inject_smart_context_features_internal(master_matrix, target_asset="GOLD")
        master_matrix = inject_smart_context_features_internal(master_matrix, target_asset="BTC")
        
        if 'DXY_Close' in master_matrix.columns:
            master_matrix['DXY_MA_24'] = master_matrix['DXY_Close'].rolling(window=24, min_periods=1).mean()
        else:
            master_matrix['DXY_MA_24'] = 100.0

        master_matrix['Time_Join'] = master_matrix.index
        historical_layers = generate_historical_macro_and_liquidity(master_matrix.index)
        historical_layers['Time_Join'] = historical_layers.index
        
        master_matrix = pd.merge_asof(master_matrix, historical_layers, on='Time_Join', direction='backward')
        master_matrix.set_index('Time_Join', inplace=True)
        master_matrix.index.name = 'Time'

        # حساب العوائد اللحظية الصافية لجميع الأصول المتواجدة في المصفوفة
        for asset_name in market_symbols.keys():
            if f'{asset_name}_Close' in master_matrix.columns:
                master_matrix[f'{asset_name}_Return'] = master_matrix[f'{asset_name}_Close'].pct_change()
            
        master_matrix.ffill(inplace=True)
        master_matrix.bfill(inplace=True)
        master_matrix.dropna(inplace=True)
        
        # حفظ المصفوفة البكر الجديدة والمحدثة في الكاش لمنع استهلاك الطلبات الحية المتكررة
        if not master_matrix.empty and len(master_matrix) > 100:
            master_matrix.to_parquet(cache_file)
            print("📊 [Data Ingestion] تم توليد وتحديث مصفوفة العوائد الكونية الصافية بنجاح واستقرار فائق.")
        return master_matrix
    except Exception as e:
        print(f"❌ خطأ معالجة المصفوفة: {e}")
        if os.path.exists(cache_file):
            return pd.read_parquet(cache_file)
        return None