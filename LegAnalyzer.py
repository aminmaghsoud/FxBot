import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO
import math
import os

class LegAnalyzer():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
      data_dir = "C:\\Fxbot\\config"
      csv_file = None
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
          self.setup_data_directory()
          self.initialize_csv()

      def detect_fake_breakout(self, FrameRatesM5, SymbolInfo, leg_type, breakout_price):
          """
          تشخیص شکست کاذب بر اساس چند معیار
          """
          try:
              # 1. بررسی حجم معاملات
              breakout_volume = FrameRatesM5.iloc[-2]['tick_volume']
              avg_volume = FrameRatesM5.iloc[-5:-2]['tick_volume'].mean()
              volume_ratio = breakout_volume / avg_volume
              
              # 2. بررسی سایه کندل شکست
              candle = FrameRatesM5.iloc[-2]
              body_size = abs(candle['close'] - candle['open'])
              upper_shadow = candle['high'] - max(candle['open'], candle['close'])
              lower_shadow = min(candle['open'], candle['close']) - candle['low']
              
              # 3. بررسی فاصله از قیمت شکست
              if leg_type == 'bullish':
                  distance = (breakout_price - PublicVarible.BaseroofLA) / SymbolInfo.point
              else:
                  distance = (PublicVarible.BasefloorLA - breakout_price) / SymbolInfo.point
              
              # 4. بررسی مومنتوم
              momentum = self.calculate_momentum(FrameRatesM5, SymbolInfo)
              
              # معیارهای تشخیص شکست کاذب
              fake_breakout_criteria = {
                  'low_volume': volume_ratio < 1.2,  # حجم معاملات کمتر از 20% میانگین
                  'long_shadow': (upper_shadow > body_size * 2) or (lower_shadow > body_size * 2),  # سایه بلند
                  'small_distance': distance < 5,  # فاصله کم از قیمت شکست
                  'weak_momentum': abs(momentum) < 0.5  # مومنتوم ضعیف
              }
              
              # اگر حداقل 2 معیار شکست کاذب برقرار باشد
              fake_breakout_count = sum(1 for value in fake_breakout_criteria.values() if value)
              is_fake_breakout = fake_breakout_count >= 2
              
              return is_fake_breakout
              
          except Exception as e:
              error_msg = f"خطا در تشخیص شکست کاذب: {str(e)}"
              print(error_msg)
              PromptToTelegram(Text=error_msg)
              return False

      def setup_data_directory(self):
          """
          ایجاد پوشه config اگر وجود نداشته باشد
          """
          try:
              # ایجاد پوشه config اگر وجود نداشته باشد
              if not os.path.exists(self.data_dir):
                  os.makedirs(self.data_dir)
                  print(f"پوشه {self.data_dir} ایجاد شد")
              
              # تنظیم مسیر کامل فایل CSV
              self.csv_file = os.path.join(self.data_dir, "leg_analysis.csv")
              #print(f"مسیر فایل CSV: {self.csv_file}")
              
          except Exception as e:
              error_msg = f"خطا در ایجاد پوشه config: {str(e)}"
              #print(error_msg)
              PromptToTelegram(Text=error_msg)

      def initialize_csv(self):
          """
          ایجاد فایل CSV اگر وجود نداشته باشد
          """
          try:
              if not os.path.exists(self.csv_file):
                  #print("فایل CSV وجود ندارد. در حال ایجاد...")
                  columns = [
                      'datetime',              # زمان تشکیل لگ
                      'pair',                  # جفت ارز
                      'leg_type',              # نوع لگ (صعودی/نزولی)
                      'leg_height',            # ارتفاع لگ
                      'leg_candles_count',     # تعداد کندل‌های لگ
                      'range_height',          # ارتفاع رنج
                      'range_to_leg_ratio',    # نسبت رنج به لگ
                      'breakout_candle_size',  # اندازه کندل شکست
                      'breakout_volume',       # حجم معاملات کندل شکست
                      'trend_strength',        # قدرت روند (1, 2, -1, -2)
                      'head_shoulder_pattern', # الگوی سر و شانه (0, 1)
                      'momentum',              # مومنتوم قیمت
                      'fake_breakout',         # شکست کاذب (True/False)
                      'result'                 # نتیجه (موفق/ناموفق)
                  ]
                  df = PD.DataFrame(columns=columns)
                  df.to_csv(self.csv_file, index=False)
                  #print(f"فایل CSV در مسیر {self.csv_file} ایجاد شد")
              else:
                 # print(f"فایل CSV در مسیر {self.csv_file} از قبل وجود دارد")
              
          except Exception as e:
              error_msg = f"خطا در ایجاد فایل CSV: {str(e)}"
              print(error_msg)
              PromptToTelegram(Text=error_msg)

      def save_to_csv(self, leg_data):
          """
          ذخیره اطلاعات لگ در فایل CSV
          """
          try:
              # خواندن فایل CSV موجود
              df = PD.read_csv(self.csv_file)
              
              # اضافه کردن داده جدید با استفاده از concat
              new_df = PD.DataFrame([leg_data])
              df = PD.concat([df, new_df], ignore_index=True)
              
              # ذخیره در فایل
              df.to_csv(self.csv_file, index=False)
              
          except Exception as e:
              error_msg = f"خطا در ذخیره اطلاعات در CSV: {str(e)}"
              print(error_msg)
              PromptToTelegram(Text=error_msg)

      def update_trade_result(self, leg_data, FrameRatesM5, SymbolInfo):
          """
          به‌روزرسانی نتیجه معامله در فایل CSV
          """
          try:
              # خواندن فایل CSV
              df = PD.read_csv(self.csv_file)
              
              # پیدا کردن ردیف مربوط به این لگ
              mask = (df['datetime'] == leg_data['datetime']) & (df['pair'] == leg_data['pair'])
              if not mask.any():
                  return
              
              # محاسبه نتیجه معامله
              breakout_price = leg_data['breakout_candle_size']
              if leg_data['leg_type'] == 'bullish':
                  # برای لگ صعودی
                  target_price = PublicVarible.BaseroofLA + (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA))
                  stop_loss = PublicVarible.BasefloorLA - (SymbolInfo.point * 50)
                  
                  # بررسی 5 کندل بعد از شکست
                  for i in range(-5, 0):
                      current_price = FrameRatesM5.iloc[i]['close']
                      if current_price >= target_price:
                          df.loc[mask, 'result'] = 'success'
                          break
                      elif current_price <= stop_loss:
                          df.loc[mask, 'result'] = 'failure'
                          break
              else:
                  # برای لگ نزولی
                  target_price = PublicVarible.BasefloorLA - (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA))
                  stop_loss = PublicVarible.BaseroofLA + (SymbolInfo.point * 50)
                  
                  # بررسی 5 کندل بعد از شکست
                  for i in range(-5, 0):
                      current_price = FrameRatesM5.iloc[i]['close']
                      if current_price <= target_price:
                          df.loc[mask, 'result'] = 'success'
                          break
                      elif current_price >= stop_loss:
                          df.loc[mask, 'result'] = 'failure'
                          break
              
              # ذخیره تغییرات در فایل CSV
              df.to_csv(self.csv_file, index=False)
              
          except Exception as e:
              error_msg = f"خطا در به‌روزرسانی نتیجه معامله: {str(e)}"
              print(error_msg)
              PromptToTelegram(Text=error_msg)

      def calculate_momentum(self, FrameRatesM5, SymbolInfo):
          """
          محاسبه مومنتوم بر اساس تغییرات قیمت و حجم معاملات
          """
          try:
              # محاسبه تغییرات قیمت در 5 کندل آخر
              price_changes = []
              for i in range(-5, 0):
                  if i < -1:  # برای جلوگیری از خطای ایندکس
                      change = (FrameRatesM5.iloc[i]['close'] - FrameRatesM5.iloc[i-1]['close']) / SymbolInfo.point
                      price_changes.append(change)
              
              # محاسبه میانگین تغییرات قیمت
              avg_price_change = sum(price_changes) / len(price_changes)
              
              # محاسبه تغییرات حجم در 5 کندل آخر
              volume_changes = []
              for i in range(-5, 0):
                  if i < -1:
                      change = FrameRatesM5.iloc[i]['tick_volume'] - FrameRatesM5.iloc[i-1]['tick_volume']
                      volume_changes.append(change)
              
              # محاسبه میانگین تغییرات حجم
              avg_volume_change = sum(volume_changes) / len(volume_changes)
              
              # محاسبه مومنتوم نهایی
              momentum = (avg_price_change * avg_volume_change) / 1000  # تقسیم بر 1000 برای نرمال‌سازی
              
              return round(momentum, 2)
              
          except Exception as e:
              error_msg = f"خطا در محاسبه مومنتوم: {str(e)}"
              print(error_msg)
              PromptToTelegram(Text=error_msg)
              return 0

##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ LegAnalyzer  ")
          # ارسال پیام
          
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 20)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)

           
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()

             trend_C = 0
             close_C = FrameRatesM5.iloc[-2]['close']
             high_C = FrameRatesM5.iloc[-2]['high'] 
             low_C = FrameRatesM5.iloc[-2]['low']
             high_C_O = FrameRatesM5.iloc[-3]['high'] 
             low_C_O = FrameRatesM5.iloc[-3]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             
             
#########################  بررسی قدرت کندل خروج    #########################    
             LowerLLA = PublicVarible.LowerLLA
             HigherHLA = PublicVarible.HigherHLA
             #print(f"Lower low = {PublicVarible.LowerLLA} \nhigher high = {PublicVarible.HigherHLA}")

             if  close_C >= One_third_UP and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down and close_C < low_C_O :
                 trend_C = -1
             elif close_C > One_third_Down and close_C < One_third_UP and close_C > high_C_O :
                 trend_C = +2
             elif close_C > One_third_Down and close_C < One_third_UP and  close_C < low_C_O :
                 trend_C = -2
                 
             """if trend_C == 0 :
                  print("** Directional Pattern  **")
             elif trend_C == +1 : 
                  print("** Strong Bullish Candlestick Pattern **")
             elif trend_C == +2 : 
                  print("**Weak Bullish Candlestick Pattern **")
             elif trend_C == -1 : 
                  print("** Strong Bearish Candlestick Pattern **")
             elif trend_C == -2 : 
                  print("** Weak Bearish Candlestick Pattern **")
             """

             #### شناسایی لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             Text = None
             if high_C > (high_C_O ) :# and (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low']) : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H :# and Now_c_L < Old_c_L :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
            #### مقداردهی سقف و کف BOS
             if count > 2 : 
                PublicVarible.Leg_startLA = FrameRatesM5.iloc[current_index]['high']
                PublicVarible.high_low_diffLA  = round((abs( FrameRatesM5['low'].iloc[current_index : -1 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point) / 10, 2) / PublicVarible.high_low_diffLA  * 1000,1) < 50 : 
                 leg_contorol = 150
                 if PublicVarible.high_low_diffLA  > (leg_contorol) and PublicVarible.high_low_diffLA  < (1200 ) : 
                  PublicVarible.HigherHLA = high_C 
                  PublicVarible.LowerLLA = low_C 
                  PublicVarible.BasefloorLA = FrameRatesM5['low'].iloc[current_index : -1 ].min() 
                  PublicVarible.BaseroofLA = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.range_heightLA = round(abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)
                  
                  # ذخیره اطلاعات لگ نزولی
                  leg_data = {
                      'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      'pair': self.Pair,
                      'leg_type': 'bearish',
                      'leg_height': PublicVarible.high_low_diffLA,
                      'leg_candles_count': count,
                      'range_height': PublicVarible.range_heightLA,
                      'range_to_leg_ratio': round(PublicVarible.range_heightLA / PublicVarible.high_low_diffLA * 100, 2),
                      'breakout_candle_size': round(abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / (SymbolInfo.point), 2),
                      'breakout_volume': FrameRatesM5.iloc[-2]['tick_volume'],
                      'trend_strength': trend_C,
                      'head_shoulder_pattern': PublicVarible.HS_DownLA,
                      'momentum': self.calculate_momentum(FrameRatesM5, SymbolInfo),
                      'fake_breakout': self.detect_fake_breakout(FrameRatesM5, SymbolInfo, 'bearish', close_C),
                      'result': 'pending'  # وضعیت اولیه: در انتظار نتیجه
                  }
                  self.save_to_csv(leg_data)
                  self.update_trade_result(leg_data, FrameRatesM5, SymbolInfo)

             ## شناسایی لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             Text = None       
             if (low_C < low_C_O - (SymbolInfo.point * 2)) :# and (FrameRatesM5.iloc[-2]['high'] < FrameRatesM5.iloc[-3]['high']) :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       if  Now_c_L > Old_c_L :# and Now_c_H > Old_c_H :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
            ## مقداردهی سقف و کف BOS
             if count > 2 : 
              PublicVarible.Leg_startLA = FrameRatesM5.iloc[current_index]['low']
              PublicVarible.high_low_diffLA  = round((abs(FrameRatesM5.iloc[current_index : -1]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
              if  round((round(abs((FrameRatesM5.iloc[current_index : -1]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / PublicVarible.high_low_diffLA * 1000,1) < 50 :
                 leg_contorol = 150
                 if PublicVarible.high_low_diffLA  > (leg_contorol) and PublicVarible.high_low_diffLA  < (1200 ) : 
                  PublicVarible.HigherHLA = high_C 
                  PublicVarible.LowerLLA = low_C  
                  PublicVarible.BaseroofLA = FrameRatesM5.iloc[current_index : -1]['high'].max()
                  PublicVarible.BasefloorLA = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.range_heightLA = round(abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)
                  
                  # ذخیره اطلاعات لگ صعودی
                  leg_data = {
                      'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      'pair': self.Pair,
                      'leg_type': 'bullish',
                      'leg_height': PublicVarible.high_low_diffLA,
                      'leg_candles_count': count,
                      'range_height': PublicVarible.range_heightLA,
                      'range_to_leg_ratio': round(PublicVarible.range_heightLA / PublicVarible.high_low_diffLA * 100, 2),
                      'breakout_candle_size': round(abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / (SymbolInfo.point), 2),
                      'breakout_volume': FrameRatesM5.iloc[-2]['tick_volume'],
                      'trend_strength': trend_C,
                      'head_shoulder_pattern': PublicVarible.HS_UpLA,
                      'momentum': self.calculate_momentum(FrameRatesM5, SymbolInfo),
                      'fake_breakout': self.detect_fake_breakout(FrameRatesM5, SymbolInfo, 'bullish', close_C),
                      'result': 'pending'  # وضعیت اولیه: در انتظار نتیجه
                  }
                  self.save_to_csv(leg_data)
                  self.update_trade_result(leg_data, FrameRatesM5, SymbolInfo)

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.BaseroofLA != 0 and close_C < PublicVarible.BaseroofLA and close_C > PublicVarible.BasefloorLA : 
               if high_C > PublicVarible.HigherHLA : 
                  PublicVarible.HigherHLA = high_C 
               if low_C < PublicVarible.LowerLLA: 
                  PublicVarible.LowerLLA = low_C
             elif PublicVarible.BasefloorLA == 0 : 
                  PublicVarible.LowerLLA = PublicVarible.HigherHLA  = 0

################################### بررسی الگوی سر و شانه #####################################

             CH2 = FrameRatesM5.iloc[-2]['high']
             CL2 = FrameRatesM5.iloc[-2]['low']
             CC2 = FrameRatesM5.iloc[-2]['close']

             CH3 = FrameRatesM5.iloc[-3]['high']
             CL3 = FrameRatesM5.iloc[-3]['low']
             CC3 = FrameRatesM5.iloc[-3]['close']

             CH4 = FrameRatesM5.iloc[-4]['high']
             CL4 = FrameRatesM5.iloc[-4]['low']

             CH5 = FrameRatesM5.iloc[-5]['high']
             CL5 = FrameRatesM5.iloc[-5]['low']

             if PublicVarible.BasefloorLA == 0 : PublicVarible.HS_UpLA = PublicVarible.HS_DownLA = 0 
             elif PublicVarible.BasefloorLA != 0 and PublicVarible.HS_UpLA == 0 and PublicVarible.HS_DownLA == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                     PublicVarible.HS_DownLA = 1
               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                     PublicVarible.HS_UpLA = 1 

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.BaseroofLA and close_C < (PublicVarible.BaseroofLA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofLA != 0 :
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C >= (PublicVarible.BaseroofLA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofLA != 0 and close_C > HigherHLA : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.BaseroofLA} ")
                if  True :   
                   if trend_C == +1 : 
                       Text += f"خروج قیمت از #سقف با قدرت #زیاد توسط خریداران  🐮 \n "
                   elif trend_C == +2 : 
                       PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
#Buy                  
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.BasefloorLA - ( SymbolInfo.point * 50)  #((PublicVarible.BaseroofLA - PublicVarible.BasefloorLA)/2)  #########  تعیین حدضرر معامله #########
                TP1 = SymbolInfo.ask + (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA))
                Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                if  trend_C == +1  : 
                   if  (abs(close_C - PublicVarible.BaseroofLA) < (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) * 0.75 )):       
                     EntryPrice = SymbolInfo.ask
                     Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)      
                     Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0  

                # ذخیره اطلاعات لگ صعودی
                leg_data = {
                    'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'pair': self.Pair,
                    'leg_type': 'bullish',
                    'leg_height': PublicVarible.high_low_diffLA,
                    'leg_candles_count': count,
                    'range_height': PublicVarible.range_heightLA,
                    'range_to_leg_ratio': round(PublicVarible.range_heightLA / PublicVarible.high_low_diffLA * 100, 2),
                    'breakout_candle_size': round(abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / (SymbolInfo.point), 2),
                    'breakout_volume': FrameRatesM5.iloc[-2]['tick_volume'],
                    'trend_strength': trend_C,
                    'head_shoulder_pattern': PublicVarible.HS_UpLA,
                    'momentum': self.calculate_momentum(FrameRatesM5, SymbolInfo),
                    'fake_breakout': self.detect_fake_breakout(FrameRatesM5, SymbolInfo, 'bullish', close_C),
                    'result': 'pending'  # وضعیت اولیه: در انتظار نتیجه
                }
                self.save_to_csv(leg_data)
                self.update_trade_result(leg_data, FrameRatesM5, SymbolInfo)

#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.BasefloorLA and close_C > (PublicVarible.BasefloorLA + (SymbolInfo.point * 5)) and PublicVarible.BasefloorLA != 0 :
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C <= (PublicVarible.BasefloorLA - (SymbolInfo.point * 5)) and PublicVarible.BasefloorLA != 0 and close_C < LowerLLA : 
                print(f"price is {close_C} and Under floor {PublicVarible.BasefloorLA} ")
                if True :   
                   if trend_C == -1 : 
                       Text += f"خروج قیمت از #کف با قدرت #زیاد توسط فروشندگان 🐻 \n"
                   elif trend_C == -2 :
                        PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
#Sell
                
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.BaseroofLA + ( SymbolInfo.point * 50)  #((PublicVarible.BaseroofLA - PublicVarible.BasefloorLA)/2)                     #########  تعیین حدضرر معامله #########
                TP1 = SymbolInfo.bid - (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA))  #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofLA) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                if  (trend_C == -1 ) :
                   if  (abs(close_C - PublicVarible.BasefloorLA) < (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA)* 0.75) ) :
                     EntryPrice = SymbolInfo.bid  
                     Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofLA) / (SymbolInfo.point) / 10, 2)      
                     Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0

                # ذخیره اطلاعات لگ نزولی
                leg_data = {
                    'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'pair': self.Pair,
                    'leg_type': 'bearish',
                    'leg_height': PublicVarible.high_low_diffLA,
                    'leg_candles_count': count,
                    'range_height': PublicVarible.range_heightLA,
                    'range_to_leg_ratio': round(PublicVarible.range_heightLA / PublicVarible.high_low_diffLA * 100, 2),
                    'breakout_candle_size': round(abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / (SymbolInfo.point), 2),
                    'breakout_volume': FrameRatesM5.iloc[-2]['tick_volume'],
                    'trend_strength': trend_C,
                    'head_shoulder_pattern': PublicVarible.HS_DownLA,
                    'momentum': self.calculate_momentum(FrameRatesM5, SymbolInfo),
                    'fake_breakout': self.detect_fake_breakout(FrameRatesM5, SymbolInfo, 'bearish', close_C),
                    'result': 'pending'  # وضعیت اولیه: در انتظار نتیجه
                }
                self.save_to_csv(leg_data)
                self.update_trade_result(leg_data, FrameRatesM5, SymbolInfo)

                

      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500

