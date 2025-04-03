import pandas as pd
import numpy as np
from datetime import datetime
import os

class DataCollector:
    def __init__(self, data_file='training_data.csv'):
        """
        مقداردهی اولیه کلاس
        
        Args:
            data_file (str): نام فایل برای ذخیره داده‌ها
        """
        self.data_file = data_file
        self.initialize_data_file()
        
    def initialize_data_file(self):
        """
        ایجاد فایل داده‌ها اگر وجود نداشته باشد
        """
        if not os.path.exists(self.data_file):
            columns = [
                'datetime',          # زمان تشکیل لگ
                'pair',             # جفت ارز
                'leg_type',         # نوع لگ (صعودی/نزولی)
                'leg_height',       # ارتفاع لگ
                'range_height',     # ارتفاع رنج
                'range_to_leg_ratio', # نسبت رنج به لگ
                'num_candles',      # تعداد کندل‌های رنج
                'breakout_body_size', # اندازه بدنه کندل شکست
                'breakout_upper_wick', # سایه بالایی کندل شکست
                'breakout_lower_wick', # سایه پایینی کندل شکست
                'breakout_volume',   # حجم معاملات کندل شکست
                'pre_breakout_volume_avg', # میانگین حجم 5 کندل قبل از شکست
                'price_momentum',    # مومنتوم قیمت
                'result',           # نتیجه (ادامه روند/ریورس)
                'profit_pips',      # سود/ضرر به پیپ
                'trade_duration'     # مدت زمان معامله
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.data_file, index=False)
            
    def save_leg_data(self, data_dict):
        """
        ذخیره اطلاعات یک لگ جدید
        
        Args:
            data_dict (dict): دیکشنری حاوی اطلاعات لگ
        """
        try:
            df = pd.read_csv(self.data_file)
            new_row = pd.DataFrame([data_dict])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.data_file, index=False)
            print(f"Data saved successfully for {data_dict['pair']} at {data_dict['datetime']}")
            
        except Exception as e:
            error_msg = f"Error in save_leg_data: {str(e)}"
            print(error_msg)
            
    def prepare_training_data(self):
        """
        آماده‌سازی داده‌ها برای آموزش مدل
        
        Returns:
            DataFrame: داده‌های آماده برای آموزش
        """
        try:
            df = pd.read_csv(self.data_file)
            
            # تبدیل متغیرهای کیفی به کمی
            df['leg_type'] = df['leg_type'].map({'bullish': 1, 'bearish': 0})
            df['result'] = df['result'].map({'continuation': 1, 'reversal': 0})
            
            # حذف ستون‌های غیر ضروری
            features_df = df.drop(['datetime', 'pair', 'profit_pips', 'trade_duration'], axis=1)
            
            return features_df
            
        except Exception as e:
            error_msg = f"Error in prepare_training_data: {str(e)}"
            print(error_msg)
            return None
            
    def calculate_leg_features(self, candles_data, leg_start_index, leg_end_index):
        """
        محاسبه ویژگی‌های لگ
        
        Args:
            candles_data (DataFrame): دیتافریم کندل‌ها
            leg_start_index (int): اندیس شروع لگ
            leg_end_index (int): اندیس پایان لگ
            
        Returns:
            dict: دیکشنری حاوی ویژگی‌های محاسبه شده
        """
        try:
            leg_data = {}
            
            # محاسبه ارتفاع لگ
            leg_high = candles_data.iloc[leg_start_index:leg_end_index+1]['high'].max()
            leg_low = candles_data.iloc[leg_start_index:leg_end_index+1]['low'].min()
            leg_height = abs(leg_high - leg_low)
            
            # محاسبه مومنتوم قیمت
            close_prices = candles_data.iloc[leg_start_index:leg_end_index+1]['close']
            momentum = (close_prices.iloc[-1] - close_prices.iloc[0]) / leg_height
            
            # محاسبه میانگین حجم
            volume_avg = candles_data.iloc[leg_start_index:leg_end_index+1]['volume'].mean()
            
            leg_data.update({
                'leg_height': leg_height,
                'price_momentum': momentum,
                'pre_breakout_volume_avg': volume_avg
            })
            
            return leg_data
            
        except Exception as e:
            error_msg = f"Error in calculate_leg_features: {str(e)}"
            print(error_msg)
            return None
            
    def update_trade_result(self, entry_time, pair, result, profit_pips, duration):
        """
        به‌روزرسانی نتیجه معامله
        
        Args:
            entry_time (str): زمان ورود به معامله
            pair (str): جفت ارز
            result (str): نتیجه (continuation/reversal)
            profit_pips (float): سود/ضرر به پیپ
            duration (int): مدت زمان معامله به دقیقه
        """
        try:
            df = pd.read_csv(self.data_file)
            mask = (df['datetime'] == entry_time) & (df['pair'] == pair)
            
            if mask.any():
                df.loc[mask, 'result'] = result
                df.loc[mask, 'profit_pips'] = profit_pips
                df.loc[mask, 'trade_duration'] = duration
                df.to_csv(self.data_file, index=False)
                print(f"Trade result updated for {pair} at {entry_time}")
            
        except Exception as e:
            error_msg = f"Error in update_trade_result: {str(e)}"
            print(error_msg)
