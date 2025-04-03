import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
from datetime import datetime
import mplfinance as mpf
from io import BytesIO
from Utility import send_telegram_messages, send_telegram_photo
import PublicVarible

class SupplyDemandAIStrategy:
    def __init__(self):
        """
        مقداردهی اولیه کلاس
        """
        self.model = None
        self.scaler = StandardScaler()
        self.features = []
        self.Pair = None
        
    def extract_features(self, candles_data, breakout_candle_index):
        """
        استخراج ویژگی‌های مهم از داده‌های کندل‌ها
        
        Args:
            candles_data (DataFrame): دیتافریم حاوی اطلاعات کندل‌ها
            breakout_candle_index (int): اندیس کندل شکست
            
        Returns:
            array: آرایه‌ای از ویژگی‌های استخراج شده
        """
        try:
            features = []
            
            # ویژگی‌های کندل شکست
            breakout_candle = candles_data.iloc[breakout_candle_index]
            body_size = abs(breakout_candle['close'] - breakout_candle['open'])
            upper_wick = breakout_candle['high'] - max(breakout_candle['open'], breakout_candle['close'])
            lower_wick = min(breakout_candle['open'], breakout_candle['close']) - breakout_candle['low']
            
            features.extend([
                body_size,  # اندازه بدنه کندل شکست
                upper_wick,  # سایه بالایی
                lower_wick,  # سایه پایینی
                breakout_candle['volume']  # حجم معاملات
            ])
            
            return np.array(features)
            
        except Exception as e:
            error_msg = f"Error in extract_features: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return None
            
    def predict_breakout_direction(self, features):
        """
        پیش‌بینی جهت حرکت قیمت پس از شکست
        
        Args:
            features (array): آرایه‌ای از ویژگی‌های استخراج شده
            
        Returns:
            tuple: (جهت پیش‌بینی شده، احتمال)
        """
        try:
            if self.model is None:
                return None, 0
                
            # نرمال‌سازی ویژگی‌ها
            features_scaled = self.scaler.transform([features])
            
            # پیش‌بینی جهت
            prediction = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)
            
            return prediction[0], max(probabilities[0])
            
        except Exception as e:
            error_msg = f"Error in predict_breakout_direction: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return None, 0
            
    def calculate_entry_point(self, breakout_price, prediction, confidence):
        """
        محاسبه نقطه ورود مناسب
        
        Args:
            breakout_price (float): قیمت شکست
            prediction (int): جهت پیش‌بینی شده
            confidence (float): میزان اطمینان پیش‌بینی
            
        Returns:
            float: قیمت ورود پیشنهادی
        """
        try:
            # محاسبه فاصله مناسب برای ورود بر اساس میزان اطمینان
            entry_distance = 10 * (1 - confidence)  # مثال: هر چه اطمینان کمتر، فاصله بیشتر
            
            if prediction == 1:  # ادامه روند صعودی
                return breakout_price + entry_distance
            else:  # ادامه روند نزولی
                return breakout_price - entry_distance
                
        except Exception as e:
            error_msg = f"Error in calculate_entry_point: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return None
            
    def calculate_risk_reward(self, entry_price, prediction, atr):
        """
        محاسبه حد ضرر و حد سود
        
        Args:
            entry_price (float): قیمت ورود
            prediction (int): جهت پیش‌بینی شده
            atr (float): شاخص ATR
            
        Returns:
            tuple: (حد ضرر، حد سود)
        """
        try:
            # استفاده از ATR برای تنظیم حد ضرر و حد سود
            stop_loss_distance = 1.5 * atr
            take_profit_distance = 3 * atr  # نسبت ریسک به ریوارد 1:2
            
            if prediction == 1:  # ادامه روند صعودی
                stop_loss = entry_price - stop_loss_distance
                take_profit = entry_price + take_profit_distance
            else:  # ادامه روند نزولی
                stop_loss = entry_price + stop_loss_distance
                take_profit = entry_price - take_profit_distance
                
            return stop_loss, take_profit
            
        except Exception as e:
            error_msg = f"Error in calculate_risk_reward: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return None, None
            
    def should_enter_trade(self, confidence, market_conditions):
        """
        تصمیم‌گیری برای ورود به معامله
        
        Args:
            confidence (float): میزان اطمینان پیش‌بینی
            market_conditions (dict): شرایط فعلی بازار
            
        Returns:
            bool: آیا باید وارد معامله شد
        """
        try:
            # شرایط ورود به معامله
            if confidence < 0.7:  # حداقل 70% اطمینان
                return False
                
            # بررسی شرایط بازار
            if market_conditions.get('volatility', 0) > 0.5:  # نوسان بیش از حد
                return False
                
            return True
            
        except Exception as e:
            error_msg = f"Error in should_enter_trade: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return False
            
    def train_model(self, training_data):
        """
        آموزش مدل با داده‌های تاریخی
        
        Args:
            training_data (DataFrame): داده‌های آموزشی
        """
        try:
            X = training_data.drop('target', axis=1)
            y = training_data['target']
            
            # نرمال‌سازی ویژگی‌ها
            X_scaled = self.scaler.fit_transform(X)
            
            # ایجاد و آموزش مدل
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)
            
            # ذخیره مدل
            joblib.dump(self.model, 'supply_demand_ai_model.joblib')
            joblib.dump(self.scaler, 'supply_demand_scaler.joblib')
            
        except Exception as e:
            error_msg = f"Error in train_model: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            
    def load_model(self):
        """
        بارگذاری مدل ذخیره شده
        """
        try:
            self.model = joblib.load('supply_demand_ai_model.joblib')
            self.scaler = joblib.load('supply_demand_scaler.joblib')
            return True
            
        except Exception as e:
            error_msg = f"Error in load_model: {str(e)}"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return False
