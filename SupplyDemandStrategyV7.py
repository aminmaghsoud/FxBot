﻿import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV7():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair !='AUDJPYb' : return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V7 M5  ")
          # ارسال پیام
          
          Time_Signal = 1
          high_low_diff = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)


             buy_positions_with_open_prices = get_buy_positions_with_open_prices()
             if buy_positions_with_open_prices:
                      for ticket, open_price in buy_positions_with_open_prices.items():
                          position_data = {
                              "symbol": self.Pair,  # نماد
                              "ticket": ticket,     # شماره تیکت موقعیت
                          }
                          positions = MT5.positions_get()
                          for position_info in positions:
                             if position_info.ticket == ticket and position_info.symbol == self.Pair :
                                 entry_price = position_info.price_open
                                 take_profit = position_info.tp
                                 stoploss = position_info.sl
                                 
                                 if  SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.90 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status") 
                                 elif SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.75 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = abs(abs(entry_price - take_profit) * 0.25 + entry_price) #(entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.50 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = entry_price
                                     # اعمال تغییرات
                                     #ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")
             
             sell_positions_with_open_prices = get_sell_positions_with_open_prices()
             if sell_positions_with_open_prices:
                      for ticket, open_price in sell_positions_with_open_prices.items():
                          position_data = {
                              "symbol": self.Pair,  # نماد
                              "ticket": ticket,     # شماره تیکت موقعیت
                          }
                          positions = MT5.positions_get()
                          for position_info in positions:
                             if position_info.ticket == ticket and position_info.symbol == self.Pair :
                                 entry_price = position_info.price_open
                                 take_profit = position_info.tp
                                 stoploss = position_info.sl
                                 if SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.90 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.75 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = abs(abs(entry_price - take_profit) * 0.25 - entry_price)
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.50 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = entry_price
                                     # اعمال تغییرات
                                     #ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

             buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
             if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return
             sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
             if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             # دریافت زمان فعلی
             current_time = time.time()
             current_datetime = datetime.now()
             # تعریف بازه‌های زمانی ممنوعه
             restricted_time_ranges = [
                (0, 0, 1, 30),    
                (8, 0, 11, 0),  
                (15, 45, 18, 45),  
                (22, 0, 23, 59) 
             ]
             # بررسی اینکه آیا ساعت جاری در یکی از بازه‌های ممنوعه است یا خیر
             in_restricted_time = any(
                start_h * 60 + start_m <= current_datetime.hour * 60 + current_datetime.minute <= end_h * 60 + end_m
                for start_h, start_m, end_h, end_m in restricted_time_ranges
             )

             restricted_hours = {13, 19}
             if current_datetime.minute == 0 and current_datetime.hour in restricted_hours:
                #PublicVarible.CanOpenOrder = False
                PublicVarible.risk = 1

             if in_restricted_time or not PublicVarible.CanOpenOrder :
                 Botdashboard(4, self.Pair)
                 Time_Signal = 0

             #ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
             #ATR_Value = ATR.iloc[-1]
             #print("ATR_Value" , ATR_Value)
             ATR_Value = 1
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             if current_time - PublicVarible.BasetimeA >= 2100 and PublicVarible.BasetimeA != 0 and PublicVarible.BasefloorA != 0: 
                PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0  
                PublicVarible.BasetimeA = 0

             #if current_time - PublicVarible.Limittime >= 900 and PublicVarible.Limittime != 0 : 
                #delete_all_limit_orders()  
                #PromptToTelegram(f"⚠️ بعلت طولانی کردن زمان باز کردن لیمیت ، سفارش حذف شد!")
                #PublicVarible.Limittime = 0

             #print("PublicVarible.BasetimeA:",PublicVarible.BasetimeA)
             #print("PublicVarible.Limittime:",PublicVarible.Limittime)
             trend_C = 0
             close_C = FrameRatesM5.iloc[-2]['close']
             high_C = FrameRatesM5.iloc[-2]['high'] 
             low_C = FrameRatesM5.iloc[-2]['low']
             high_C_O = FrameRatesM5.iloc[-3]['high'] 
             low_C_O = FrameRatesM5.iloc[-3]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             
             
#########################  بررسی قدرت کندل خروج    #########################    
             LowerLA = PublicVarible.LowerLA
             HigherHA = PublicVarible.HigherHA
             print(f"Lower low = {PublicVarible.LowerLA} \nhigher high = {PublicVarible.HigherHA}")

             if  close_C >= One_third_UP and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down and close_C < low_C_O :
                 trend_C = -1
             elif close_C > One_third_Down and close_C < One_third_UP and close_C > high_C_O :
                 trend_C = +2
             elif close_C > One_third_Down and close_C < One_third_UP and  close_C < low_C_O :
                 trend_C = -2
                 
             if trend_C == 0 :
                  print("** Directional Pattern  **")
             elif trend_C == +1 : 
                  print("** Strong Bullish Candlestick Pattern **")
             elif trend_C == +2 : 
                  print("**Weak Bullish Candlestick Pattern **")
             elif trend_C == -1 : 
                  print("** Strong Bearish Candlestick Pattern **")
             elif trend_C == -2 : 
                  print("** Weak Bearish Candlestick Pattern **")

             print(f"\n BaseroofA : {PublicVarible.BaseroofA}")
             print("Close -2 : " , close_C)
             print("BasefloorA : " , PublicVarible.BasefloorA)
             

             #### شناسایی لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
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
                high_low_diff = round((abs( FrameRatesM5['low'].iloc[current_index : -1 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if ((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point)) / high_low_diff * 100 ) < 50 : 
                 if ATR_Value <= 1 : 
                  leg_contorol = (150 * ATR_Value)
                 else : leg_contorol = 200 

                 if high_low_diff > (leg_contorol) and high_low_diff < (1200 * ATR_Value) : # (200 * ATR_Value * 0.9)
                  PublicVarible.HigherHA = high_C 
                  PublicVarible.LowerLA = low_C 
                  PublicVarible.BasefloorA = FrameRatesM5['low'].iloc[current_index : -1 ].min() 
                  PublicVarible.BaseroofA = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.BasetimeA = current_time
                  PublicVarible.range_heightA = round(abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA) / (SymbolInfo.point) / 10, 2)
                  print(f"Down high_low_diff: {high_low_diff} and BaseroofA: {PublicVarible.BaseroofA} and BasefloorA: {PublicVarible.BasefloorA} and Range arraye: {abs(PublicVarible.BasefloorA - PublicVarible.BaseroofA) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if round(PublicVarible.range_heightA / high_low_diff * 1000,1) > 50 :
                     PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                  elif current_time - PublicVarible.last_execution_timeA >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightA} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightA / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.BaseroofA} $ \n"
                   Text += f"کف رنج : {PublicVarible.BasefloorA} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightA , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)"
                   #PromptToTelegram(Text)
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                  # results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   PublicVarible.last_execution_timeA = current_time


             ## شناسایی لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
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
              high_low_diff = round((abs(FrameRatesM5.iloc[current_index : -1]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
              if ((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point)) / high_low_diff * 100 ) < 50 : 
                 if ATR_Value <= 1 : 
                  leg_contorol = (150 * ATR_Value)
                 else : leg_contorol = 200 

                 if high_low_diff > (leg_contorol) and high_low_diff < (1200 * ATR_Value) : 
                  PublicVarible.HigherHA = high_C 
                  PublicVarible.LowerLA = low_C  
                  PublicVarible.BaseroofA = FrameRatesM5.iloc[current_index : -1]['high'].max() 
                  PublicVarible.BasefloorA = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.BasetimeA = current_time
                  PublicVarible.range_heightA = round(abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA) / (SymbolInfo.point) / 10, 2)
                  print(f"Up high_low_diff: {high_low_diff} and BaseroofA: {PublicVarible.BaseroofA} and BasefloorA: {PublicVarible.BasefloorA} and Range arraye: {abs(PublicVarible.BasefloorA - PublicVarible.BaseroofA) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if round(PublicVarible.range_heightA / high_low_diff * 1000,1) > 50 :
                     PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                  elif current_time - PublicVarible.last_execution_timeA >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightA} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightA / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.BaseroofA} $ \n"
                   Text += f"کف رنج : {PublicVarible.BasefloorA} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightA , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)"
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   #PromptToTelegram(Text)
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeA = current_time

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.BaseroofA != 0 and close_C < PublicVarible.BaseroofA and close_C > PublicVarible.BasefloorA : 
               if high_C > PublicVarible.HigherHA : 
                  PublicVarible.HigherHA = high_C 
               if low_C < PublicVarible.LowerLA: 
                  PublicVarible.LowerLA = low_C
             elif PublicVarible.BasefloorA == 0 : 
                  PublicVarible.LowerLA = PublicVarible.HigherHA  = 0

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

             if PublicVarible.BasefloorA == 0 : PublicVarible.HS_UpA = PublicVarible.HS_DownA = 0 
             elif PublicVarible.BasefloorA != 0 and PublicVarible.HS_UpA == 0 and PublicVarible.HS_DownA == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                     PublicVarible.HS_DownA = 1
               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                     PublicVarible.HS_UpA = 1 

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.BaseroofA and close_C < (PublicVarible.BaseroofA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofA != 0 :
                PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C >= (PublicVarible.BaseroofA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofA != 0 and close_C > HigherHA : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.BaseroofA} ")
                if current_time - PublicVarible.last_execution_timeAS  >= 300:   
                   Text = f"#Buy Position in {self.Pair} \n \n"
                   Text += f"price:{close_C}$ 🔺Upper Roof {PublicVarible.BaseroofA}$ \n\n "
                   if trend_C == +1 : 
                       Text += f"خروج قیمت از #سقف با قدرت #زیاد توسط خریداران  🐮 \n "
                       if PublicVarible.HS_DownA == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_UpA == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                   elif trend_C == +2 : 
                       Text += f"خروج قیمت از #سقف با قدرت #معمولی توسط خریداران 🐮 \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                       if PublicVarible.HS_DownA == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_UpA == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                       PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                      Text += f" قدرت فروشنده و خریدار #برابر است 🏓 \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                      Text += f" وضعیت خروج قیمت #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                   #PromptToTelegram(Text)  
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   PublicVarible.last_execution_timeAS = current_time 
#Buy
                
                     
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.BasefloorA - ( SymbolInfo.point * 70)  #((PublicVarible.BaseroofA - PublicVarible.BasefloorA)/2)  #########  تعیین حدضرر معامله #########
                TP1 =  SymbolInfo.ask + (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA))# SymbolInfo.bid + ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorA) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BaseroofA)) - (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA)*0.75)} (If NEG T is True)" 
                write_trade_info_to_file(self.Pair ,"Buy", SymbolInfo.ask, SL, TP1, TextN )

                if (abs(close_C - PublicVarible.BaseroofA) < (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA) * 0.75 )) and (trend_C == +1 ) and Time_Signal == 1 : # and PublicVarible.hmaSignal == 1 :
                  Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.ask
                  Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorA) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                  if trend_C == 2 : Volume = round(Volume/2,2)
                  #OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V8 AUD ")
                
                  EntryPrice = (PublicVarible.BaseroofA + PublicVarible.BasefloorA)/2
                  #OrderBuyLimit(Pair= self.Pair, Volume= Volume/2 , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")
                  PromptToTelegram(f"🚨🚨 \n سفارش #خرید معوق در قیمت \n TP : {TP1} \n Price : {EntryPrice} \n SL : {SL}")
                  PublicVarible.Limittime = current_time
                else : 
                   TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                   TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BaseroofA)) - (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA)*0.75)} (If NEG T is True)" 
                   write_None(self.Pair , TextN )

                PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.BasefloorA and close_C > (PublicVarible.BasefloorA + (SymbolInfo.point * 5)) and PublicVarible.BasefloorA != 0 :
                PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C <= (PublicVarible.BasefloorA - (SymbolInfo.point * 5)) and PublicVarible.BasefloorA != 0 and close_C < LowerLA : 
                print(f"price is {close_C} and Under floor {PublicVarible.BasefloorA} ")
                if current_time - PublicVarible.last_execution_timeAS >= 300:   
                   Text = f"#Sell Position in {self.Pair} \n\n"
                   Text += f"price:{close_C}$ 🔻Under floor {PublicVarible.BasefloorA}$ \n\n "
                   if trend_C == -1 : 
                       Text += f"خروج قیمت از #کف با قدرت #زیاد توسط فروشندگان 🐻 \n"
                       if PublicVarible.HS_DownA == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_UpA == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                   elif trend_C == -2 :
                       Text +=  f"خروج قیمت از #کف با قدرت #معمولی توسط فروشندگان 🐻 \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                       if PublicVarible.HS_DownA == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_UpA == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                       PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                      Text += f" قدرت فروشنده و خریدار #برابر است 🏓 \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0
                      Text += f" وضعیت خروج قیمت #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   #PromptToTelegram(Text)
                  # results = send_telegram_messages(Text, PublicVarible.chat_ids)  
                   PublicVarible.last_execution_timeAS = current_time  
#Sell
                
                
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.BaseroofA + ( SymbolInfo.point * 70)  #((PublicVarible.BaseroofA - PublicVarible.BasefloorA)/2) #########  تعیین حدضرر معامله #########
                TP1 = SymbolInfo.bid - (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA))  #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofA) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BasefloorA)) - (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA)*0.75)} (If NEG T is True)\n" 
                write_trade_info_to_file(self.Pair ,"Sell", SymbolInfo.bid  , SL, TP1, TextN )
                
                if (abs(close_C - PublicVarible.BasefloorA) < (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA)* 0.75) ) and (trend_C == -1 ) and Time_Signal == 1 : #and PublicVarible.hmaSignal == -1:
                  Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.bid  
                  Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofA) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                  if trend_C == -2 : Volume = round(Volume/2,2)
                  #OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V7 AUD")

                  EntryPrice = (PublicVarible.BaseroofA + PublicVarible.BasefloorA)/2
                  #OrderSellLimit(Pair= self.Pair, Volume= Volume/2 , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V9 - M5")
                  PromptToTelegram(f"🚨🚨 \n سفارش #فروش معوق در قیمت \n SL : {SL} \n Price : {EntryPrice} \n TP : {TP1}")
                  PublicVarible.Limittime = current_time

                else : 
                    TextN = f"\n self.Pair | pos = Sell | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BasefloorA)) - (abs(PublicVarible.BaseroofA - PublicVarible.BasefloorA)*0.75)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                PublicVarible.BaseroofA = PublicVarible.BasefloorA = 0

                

      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500