import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV2():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M5 XAUUSDb ")
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 100)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty: 
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)

             RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 100)
             if RatesM30 is not None:
                FrameRatesM30 = PD.DataFrame(RatesM30)
                if not FrameRatesM30.empty: 
                   FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
                   FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
                   FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)

             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 10000)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
            

            # شناسایی لگ
             leg_info = detect_leg(FrameRatesM5 , SymbolInfo)
             print("🔍 Leg Info:", leg_info)

          # تحلیل قدرت بازار از سه تایم‌فریم
             market_power = analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30)
             print("📊 Market Power:", market_power)

          # استخراج ویژگی‌ها برای آموزش
             features = extract_leg_and_market_features(leg_info, market_power)
             print("🧠 Extracted Features:", features)


##############################################################################################################################################################

def detect_leg(FrameRatesM5, SymbolInfo):
    high_C = FrameRatesM5.iloc[-2]['high']
    low_C = FrameRatesM5.iloc[-2]['low']
    high_C_O = FrameRatesM5.iloc[-3]['high']
    low_C_O = FrameRatesM5.iloc[-3]['low']

    end_index = -16
    current_index = -3
    count = 1

    leg_type = None
    leg_start = None
    leg_end = None
    leg_height = None

    # لگ نزولی
    if high_C > high_C_O:
        while current_index > end_index:
            Now_c_H = FrameRatesM5.iloc[current_index]['high']
            Old_c_H = FrameRatesM5.iloc[current_index - 1]['high']

            if Now_c_H < Old_c_H:
                count += 1
                current_index -= 1
            else:
                break

        if count > 2:
            leg_type = 'down'
            leg_start = FrameRatesM5.iloc[current_index]['high']
            leg_end = FrameRatesM5['low'].iloc[current_index:-1].min()
            leg_height = round(abs(leg_start - leg_end) / SymbolInfo.point, 2)

    # لگ صعودی
    elif low_C < low_C_O:
        while current_index > end_index:
            Now_c_L = FrameRatesM5.iloc[current_index]['low']
            Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']

            if Now_c_L > Old_c_L:
                count += 1
                current_index -= 1
            else:
                break

        if count > 2:
            leg_type = 'up'
            leg_start = FrameRatesM5.iloc[current_index]['low']
            leg_end = FrameRatesM5['high'].iloc[current_index:-1].max()
            leg_height = round(abs(leg_end - leg_start) / SymbolInfo.point, 2)

    return {
        'leg_type': leg_type,
        'leg_start': leg_start,
        'leg_end': leg_end,
        'leg_height': leg_height,
        'leg_index': current_index
    }

##############################################################################################################################################################

def extract_leg_and_market_features(FrameRatesM5, FrameRatesM15, FrameRatesM30, SymbolInfo):
    leg_info = detect_leg(FrameRatesM5, SymbolInfo)
    if leg_info['leg_type'] is None:
        return None  # لگ معتبر پیدا نشد

    market_power = analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30)

    return {
        'leg_type': leg_info['leg_type'],
        'leg_height': leg_info['leg_height'],
        'market_trend': market_power['trend'],
        'power_score': market_power['score']
    }
##############################################################################################################################################################
def build_training_data(FrameRatesM5, FrameRatesM15, FrameRatesM30, SymbolInfo, future_window=5):
    X = []
    y = []
    max_index = len(FrameRatesM5) - future_window - 20  # 20 کندل برای شناسایی لگ و قدرت

    for i in range(60, max_index):  # از کندل 60 به بعد شروع می‌کنیم
        M5 = FrameRatesM5.iloc[i-60:i+1].copy().reset_index(drop=True)
        M15 = FrameRatesM15.iloc[i//3-20:i//3+1].copy().reset_index(drop=True)
        M30 = FrameRatesM30.iloc[i//6-20:i//6+1].copy().reset_index(drop=True)

        try:
            features = extract_leg_and_market_features(M5, M15, M30, SymbolInfo)
            if features is None:
                continue

            # برچسب: مقایسه close آینده با close فعلی
            current_close = FrameRatesM5.iloc[i]['close']
            future_close = FrameRatesM5.iloc[i + future_window]['close']
            diff = future_close - current_close

            if diff > SymbolInfo.point * 10:
                label = 'up'
            elif diff < -SymbolInfo.point * 10:
                label = 'down'
            else:
                label = 'side'

            X.append(features)
            y.append(label)
        except:
            continue

    return pd.DataFrame(X), pd.Series(y)
##############################################################################################################################################################

import pandas as pd

# نمونه اولیه تابعی که دیتای کندل‌ها را دریافت کرده و برای آموزش مدل آماده می‌کند

def extract_leg_and_market_features(FrameRatesM5, analyze_market_power):
    features = []
    targets = []

    SymbolInfo = type("Symbol", (), {"point": 0.01})  # فرضی برای تست

    for i in range(20, len(FrameRatesM5) - 5):  # بازه‌ای امن برای بررسی لگ و آینده
        current_index = i
        high_C = FrameRatesM5.iloc[i]['high']
        low_C = FrameRatesM5.iloc[i]['low']
        high_C_O = FrameRatesM5.iloc[i - 1]['high']
        low_C_O = FrameRatesM5.iloc[i - 1]['low']

        count = 1
        leg_type = 0
        leg_start_index = current_index
        leg_start_price = high_C
        leg_end_price = low_C

        # بررسی لگ نزولی
        if high_C > high_C_O:
            while current_index > i - 15:
                Now_c_H = FrameRatesM5.iloc[current_index]['high']
                Old_c_H = FrameRatesM5.iloc[current_index - 1]['high']

                if Now_c_H < Old_c_H:
                    count += 1
                    current_index -= 1
                else:
                    break
            if count > 2:
                leg_type = -1
                leg_start_index = current_index
                leg_start_price = FrameRatesM5.iloc[current_index]['high']
                leg_end_price = FrameRatesM5['low'].iloc[current_index:i].min()

        # بررسی لگ صعودی
        elif low_C < low_C_O:
            while current_index > i - 15:
                Now_c_L = FrameRatesM5.iloc[current_index]['low']
                Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']

                if Now_c_L > Old_c_L:
                    count += 1
                    current_index -= 1
                else:
                    break
            if count > 2:
                leg_type = 1
                leg_start_index = current_index
                leg_start_price = FrameRatesM5.iloc[current_index]['low']
                leg_end_price = FrameRatesM5['high'].iloc[current_index:i].max()

        if leg_type != 0:
            leg_duration = i - leg_start_index
            leg_height = abs(leg_end_price - leg_start_price)
            momentum = leg_height / leg_duration if leg_duration else 0

            # بررسی قدرت بازار در لحظه پایان لگ
            power_result = analyze_market_power(
                FrameRatesM5.iloc[i-30:i],  # M5
                FrameRatesM5.iloc[i-60:i:3],  # M15 تقریبی
                FrameRatesM5.iloc[i-120:i:6],  # M30 تقریبی
            )

            # دسته‌بندی قدرت بازار
            if power_result > 0.5:
                market_power = 1  # خریدار
            elif power_result < -0.5:
                market_power = -1  # فروشنده
            else:
                market_power = 0  # خنثی

            # بررسی رفتار بعد از لگ (مثلاً در 5 کندل آینده قیمت چه کرد)
            future_close = FrameRatesM5.iloc[i+5]['close']
            current_close = FrameRatesM5.iloc[i]['close']
            price_diff = future_close - current_close
            target = 1 if price_diff > SymbolInfo.point * 20 else 0  # سود 20 پیپی

            features.append([
                leg_type, leg_height, leg_duration, momentum, market_power
            ])
            targets.append(target)

    columns = ['leg_type', 'leg_height', 'leg_duration', 'momentum', 'market_power']
    features_df = pd.DataFrame(features, columns=columns)
    targets_series = pd.Series(targets, name='target')

    return features_df, targets_series

