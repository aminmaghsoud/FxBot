import MetaTrader5 as MT5
import pandas as pd
import numpy as np
import logging
import os
import joblib
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import xgboost as xgb
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volatility import KeltnerChannel
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import PublicVarible
from colorama import init, Fore, Back, Style
from functools import partial
import warnings
import hashlib
from imblearn.over_sampling import SMOTE
warnings.filterwarnings('ignore')

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strategy.log'),
        logging.StreamHandler()
    ]
)

# کش برای شاخص‌های تکنیکال
_technical_indicators_cache = {}

def _get_cache_key(df: pd.DataFrame) -> str:
    """ساخت کلید کش از DataFrame"""
    # تبدیل DataFrame به رشته برای هش کردن
    data_str = df.to_string()
    return hashlib.md5(data_str.encode()).hexdigest()

def calculate_class_weights(y: pd.Series) -> dict:
    """محاسبه وزن‌های کلاس برای مدیریت داده‌های نامتعادل"""
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(y)
    weights = compute_class_weight('balanced', classes=classes, y=y)
    return dict(zip(classes, weights))

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """محاسبه شاخص‌های تکنیکال با استفاده از کش"""
    # بررسی کش
    cache_key = _get_cache_key(df)
    if cache_key in _technical_indicators_cache:
        return _technical_indicators_cache[cache_key]
    
    # محاسبه شاخص‌ها
    df = df.copy()

    # شاخص‌های اصلی
    df["sma_20"] = SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["ema_50"] = EMAIndicator(close=df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
    
    # MACD
    macd = MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()
    
    # Bollinger Bands
    bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    df["bb_bbm"] = bb.bollinger_mavg()
    df["bb_bbh"] = bb.bollinger_hband()
    df["bb_bbl"] = bb.bollinger_lband()
    df["bb_width"] = (df["bb_bbh"] - df["bb_bbl"]) / df["bb_bbm"]
    
    # سایر شاخص‌ها
    df["adx"] = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14).average_true_range()
    stoch = StochasticOscillator(close=df["close"], high=df["high"], low=df["low"], window=14)
    df["stochastic"] = stoch.stoch()

    # ویژگی‌های اصلی
    df['tick_volume_ma'] = df['tick_volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['tick_volume'] / df['tick_volume_ma']
    df['price_range'] = df['high'] - df['low']
    df['price_momentum'] = df['close'].pct_change(periods=5)
    
    # تشخیص روند
    df['trend_strength'] = (df['close'] - df['sma_20']) / df['sma_20'] * 100
    df['trend_direction'] = np.where(df['trend_strength'] > 0, 1, -1)
    
    # ذخیره در کش
    _technical_indicators_cache[cache_key] = df
    return df

def get_multiple_predictions(model: xgb.XGBClassifier, X: pd.DataFrame, n_predictions: int = 5) -> List[int]:
    """دریافت پیش‌بینی‌های چندگانه"""
    predictions = []
    for i in range(1, n_predictions + 1):
        pred = model.predict(X[-i:])
        predictions.append(pred[0])
    return predictions

def save_model(model: xgb.XGBClassifier, scaler: StandardScaler, pair: str) -> None:
    """ذخیره مدل و اسکیلر"""
    model_path = f'models/{pair}_model.joblib'
    scaler_path = f'models/{pair}_scaler.joblib'
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    logging.info(f"Model and scaler saved for {pair}")

def load_model(pair: str) -> Tuple[Optional[xgb.XGBClassifier], Optional[StandardScaler]]:
    """بارگذاری مدل و اسکیلر"""
    model_path = f'models/{pair}_model.joblib'
    scaler_path = f'models/{pair}_scaler.joblib'
    
    if not (os.path.exists(model_path) and os.path.exists(scaler_path)):
        return None, None
    
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logging.info(f"Model and scaler loaded for {pair}")
        return model, scaler
    except Exception as e:
        logging.warning(f"Error loading model for {pair}: {str(e)}. Will train new model.")
        # حذف فایل‌های مدل قدیمی
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(scaler_path):
            os.remove(scaler_path)
        return None, None

def train_trend_model(df: pd.DataFrame, pair: str = None) -> Tuple[Optional[int], Optional[float], Optional[xgb.XGBClassifier]]:
    """
    آموزش مدل پیش‌بینی روند بازار
    
    Parameters:
    -----------
    df : pd.DataFrame
        داده‌های قیمتی شامل open, high, low, close, tick_volume
    pair : str, optional
        نام جفت ارز برای ذخیره/بارگذاری مدل
    
    Returns:
    --------
    Tuple[Optional[int], Optional[float], Optional[xgb.XGBClassifier]]
        پیش‌بینی، دقت مدل و مدل آموزش داده شده
    """
    try:
        # بررسی داده‌های ورودی
        required_columns = {'open', 'high', 'low', 'close', 'tick_volume'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

        # محاسبه شاخص‌های تکنیکال
        df = calculate_technical_indicators(df)

        # برچسب‌گذاری با فاصله‌های بیشتر برای روندهای بلندمدت‌تر
        df["label"] = np.where(df["close"].shift(-10) > df["close"] * 1.001, 1,  # افزایش 0.1%
                        np.where(df["close"].shift(-10) < df["close"] * 0.999, 2, 0))  # کاهش 0.1%
        df.dropna(inplace=True)

        # تعریف ویژگی‌های اصلی
        features = [
            "sma_20", "ema_50", "rsi", "macd", "macd_signal",
            "bb_bbm", "bb_bbh", "bb_bbl", "adx", "stochastic",
            "tick_volume_ma", "price_range", "trend_strength",
            "price_momentum", "volume_ratio"
        ]

        X = df[features]
        y = df["label"]

        # تقسیم داده‌ها
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # نرمال‌سازی داده‌ها
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # محاسبه وزن‌های کلاس با تنظیم مجدد
        class_weights = {
            0: 1.0,  # کاهش وزن کلاس اکثریت
            1: 2.5,  # افزایش وزن کلاس 1
            2: 2.0   # حفظ وزن کلاس 2
        }

        # آموزش مدل با پارامترهای بهینه‌شده برای داده‌های کمتر
        model = xgb.XGBClassifier(
            random_state=42,
            eval_metric='mlogloss',
            tree_method='hist',
            max_depth=7,  # افزایش عمق برای یادگیری بهتر
            min_child_weight=2,  # افزایش برای کنترل پیچیدگی
            n_estimators=400,  # افزایش تعداد درخت‌ها
            learning_rate=0.01,  # کاهش نرخ یادگیری
            subsample=0.7,  # کاهش نمونه‌گیری
            colsample_bytree=0.7,  # کاهش ویژگی‌ها برای هر درخت
            base_score=0.5,
            objective='multi:softmax',
            num_class=3,
            scale_pos_weight=1.0,
            reg_alpha=0.2,  # افزایش تنظیم L1
            reg_lambda=1.5,  # افزایش تنظیم L2
            gamma=0.2  # افزایش برای کنترل پیچیدگی
        )

        # آموزش مدل با وزن‌های کلاس
        model.fit(
            X_train_scaled, 
            y_train,
            sample_weight=[class_weights[label] for label in y_train]
        )

        # ارزیابی مدل
        y_pred = model.predict(X_test_scaled)
        accuracy = model.score(X_test_scaled, y_test)
        
        # نمایش گزارش ساده
        logging.info(f"Model Accuracy: {accuracy:.2%}")
        logging.info(f"Prediction: {y_pred[-1]}")

        # ذخیره مدل
        if pair:
            save_model(model, scaler, pair)

        # پیش‌بینی
        predictions = get_multiple_predictions(model, X_test_scaled)
        return predictions[-1], accuracy, model

    except Exception as e:
        logging.error(f"Error in train_trend_model: {str(e)}")
        return None, None, None

class SupplyDemandStrategyV1():
    Pair = ""
    TimeFrame = MT5.TIMEFRAME_M5

    def __init__(self, Pair):
        self.Pair = Pair
           
    def Main(self):
        print(Fore.LIGHTCYAN_EX, Back.BLACK, "--------------", self.Pair, Back.RESET, Fore.RESET, "------------------ Strategy V1 M5  ")
        
        SymbolInfo = MT5.symbol_info(self.Pair)
        if SymbolInfo is not None:
            RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 1000)  # کاهش تعداد کندل‌ها به 1000
            if RatesM5 is not None:
                FrameRatesM5 = pd.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                    FrameRatesM5['datetime'] = pd.to_datetime(FrameRatesM5['time'], unit='s')
                    FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                    FrameRatesM5 = FrameRatesM5.set_index(pd.DatetimeIndex(FrameRatesM5['datetime']), drop=True)

                    if(self.Pair == 'XAUUSDb'):
                        PublicVarible.prediction, PublicVarible.Accuracy, PublicVarible.model = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.prediction}, Accuracy: {PublicVarible.Accuracy:.2%}")
                    elif (self.Pair == 'CADJPYb'):
                        PublicVarible.predictionN, PublicVarible.AccuracyN, PublicVarible.modelN = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.predictionN}, Accuracy: {PublicVarible.AccuracyN:.2%}")
                    elif (self.Pair == 'BTCUSD'):
                        PublicVarible.predictionB, PublicVarible.AccuracyB, PublicVarible.modelB = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.predictionB}, Accuracy: {PublicVarible.AccuracyB:.2%}")
                    elif (self.Pair == 'USDJPYb'):
                        PublicVarible.predictionj, PublicVarible.Accuracyj, PublicVarible.modelj = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.predictionj}, Accuracy: {PublicVarible.Accuracyj:.2%}")
                    elif (self.Pair == 'EURJPYb'):
                        PublicVarible.predictionE, PublicVarible.AccuracyE, PublicVarible.modelE = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.predictionE}, Accuracy: {PublicVarible.AccuracyE:.2%}")
                    elif (self.Pair == 'CHFJPYb'):
                        PublicVarible.predictionU, PublicVarible.AccuracyU, PublicVarible.modelU = train_trend_model(FrameRatesM5, self.Pair)
                        print(f"Prediction: {PublicVarible.predictionU}, Accuracy: {PublicVarible.AccuracyU:.2%}")
                    else:
                        print(Fore.RED, Back.BLACK, "Pair not found", Back.RESET, Fore.RESET)
             
########################################################################################################