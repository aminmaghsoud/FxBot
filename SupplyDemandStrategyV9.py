﻿import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV9():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair !='XAUUSDb' : return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M5 XAUUSDb ")
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

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             # دریافت زمان فعلی
             current_time = time.time()
             current_datetime = datetime.now()
             # تعریف بازه‌های زمانی ممنوعه
             restricted_time_ranges = [
                (0, 0, 2, 0),    # 00:00 تا 02:00
                (3, 24, 3, 36),    # 03:24 تا 03:36
               # (3, 50, 4, 20),  # 04:10 تا 04:40
                (10, 25, 13, 0),  # 9:45 تا 13:00
                (15, 45, 18, 45),  # 16:00 تا 19:00
                (22, 0, 23, 59)  # 22:00 تا 23:59
             ]
             # بررسی اینکه آیا ساعت جاری در یکی از بازه‌های ممنوعه است یا خیر
             in_restricted_time = any(
                start_h * 60 + start_m <= current_datetime.hour * 60 + current_datetime.minute <= end_h * 60 + end_m
                for start_h, start_m, end_h, end_m in restricted_time_ranges
             )

             restricted_hours = {6 , 13 , 19}
             if current_datetime.minute == 0 and current_datetime.hour in restricted_hours:
                PublicVarible.CanOpenOrder = False
                PublicVarible.risk = 1
                if current_time - PublicVarible.last_execution_timeT >= 60 :
                  Text = f"⏰ Time : {current_datetime} \n"
                  Text += f"Risk changed to Safe Mode 🟢 (Low) \n"
                  Text += f"Can Open Order Stoped ... \n"
                  Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)"
                  PromptToTelegram(Text)
                  Text = f"⚠️هشدار⚠️ \n اطلاعات ارائه شده در این بات ، صرفا جنبه #آموزشی داشته و سازنده مسئولیتی در قبال ضرر احتمالی  ندارد . لطفا اصول حرفه ای معامله و مدیریت سرمایه را رعایت فرمائید . "
                  results = send_telegram_messages(Text, PublicVarible.chat_ids)
                  PublicVarible.last_execution_timeT = current_time
                  

             if in_restricted_time or not PublicVarible.CanOpenOrder :
                 Botdashboard(4, self.Pair)
                 Time_Signal = 0

             
             ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
             ATR_Value = ATR.iloc[-1]
             #print("ATR_Value" , ATR_Value)
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             if current_time - PublicVarible.Basetime >= 2100 and PublicVarible.Basetime != 0 and PublicVarible.Basefloor5 != 0: 
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0  
                #send_telegram_messages(f"⚠️پاک شدن  مقادیر سقف و کف ⚠️ \n بعلت طولانی شدن زمان خروج قیمت از رنج ، ناحیه BOS حذف گردید !", PublicVarible.chat_ids)
                PublicVarible.Basetime = 0

             if current_time - PublicVarible.Limittime >= 900 and PublicVarible.Limittime != 0 : 
                delete_all_limit_orders()  
                PromptToTelegram(f"⚠️ بعلت طولانی شدن زمان باز شدن لیمیت ، سفارش حذف شد!")
                PublicVarible.Limittime = 0

             print("PublicVarible.Basetime:",PublicVarible.Basetime)
             print("PublicVarible.Limittime:",PublicVarible.Limittime)
             trend_C = 0
             close_C = FrameRatesM5.iloc[-2]['close']
             high_C = FrameRatesM5.iloc[-2]['high'] 
             low_C = FrameRatesM5.iloc[-2]['low']
             high_C_O = FrameRatesM5.iloc[-3]['high'] 
             low_C_O = FrameRatesM5.iloc[-3]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             
             
#########################  بررسی قدرت کندل خروج    #########################    
             LowerL = PublicVarible.List_of_low
             higherH = PublicVarible.List_of_high
             print(f"Lower low = {PublicVarible.List_of_low} \nhigher high = {PublicVarible.List_of_high}")

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

             print(f"\n Baseroof5 : {PublicVarible.Baseroof5}")
             print("Close -2 : " , close_C)
             print("Basefloor5 : " , PublicVarible.Basefloor5)
             

             #### شناسایی لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Text = None
             if (high_C > (high_C_O + (SymbolInfo.point * 2))) :# and (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low']) : 
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
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff * 1000,1) < 50 : 
                 
                 if ATR_Value <= 1 : 
                  leg_contorol = (200 * ATR_Value)
                 else : leg_contorol = 250 

                 if high_low_diff > (leg_contorol) and high_low_diff < (1200 * ATR_Value) : # (200 * ATR_Value * 0.9)
                  PublicVarible.List_of_high = high_C 
                  PublicVarible.List_of_low = low_C 
                  PublicVarible.Basefloor5 = FrameRatesM5['low'].iloc[current_index : -1 ].min() 
                  PublicVarible.Baseroof5 = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.Basetime = current_time
                  PublicVarible.range_height = round(abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)
                  print(f"Down high_low_diff: {high_low_diff} and Baseroof5: {PublicVarible.Baseroof5} and Basefloor5: {PublicVarible.Basefloor5} and Range arraye: {abs(PublicVarible.Basefloor5 - PublicVarible.Baseroof5) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroof5} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloor5} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)"
                   #PromptToTelegram(Text)
                   results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   PublicVarible.last_execution_time = current_time

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
              if round((round(abs((FrameRatesM5.iloc[current_index : -1]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff * 1000,1) < 50 :
                 
                 if ATR_Value <= 1 : 
                  leg_contorol = (200 * ATR_Value)
                 else : leg_contorol = 250 

                 if high_low_diff > (leg_contorol) and high_low_diff < (1200 * ATR_Value) : 
                  PublicVarible.List_of_high = high_C 
                  PublicVarible.List_of_low = low_C  
                  PublicVarible.Baseroof5 = FrameRatesM5.iloc[current_index : -1]['high'].max() 
                  PublicVarible.Basefloor5 = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.Basetime = current_time
                  PublicVarible.range_height = round(abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)
                  print(f"Up high_low_diff: {high_low_diff} and Baseroof5: {PublicVarible.Baseroof5} and Basefloor5: {PublicVarible.Basefloor5} and Range arraye: {abs(PublicVarible.Basefloor5 - PublicVarible.Baseroof5) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroof5} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloor5} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)"
                   results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   #PromptToTelegram(Text)
                   PublicVarible.last_execution_time = current_time

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.Baseroof5 != 0 and close_C < PublicVarible.Baseroof5 and close_C > PublicVarible.Basefloor5 : 
               if high_C > PublicVarible.List_of_high : 
                  PublicVarible.List_of_high = high_C 
               if low_C < PublicVarible.List_of_low: 
                  PublicVarible.List_of_low = low_C
             elif PublicVarible.Basefloor5 == 0 : 
                  PublicVarible.List_of_low = PublicVarible.List_of_high  = 0

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

             if PublicVarible.Basefloor5 == 0 : PublicVarible.HS_Up = PublicVarible.HS_Down = 0 
             elif PublicVarible.Basefloor5 != 0 and PublicVarible.HS_Up == 0 and PublicVarible.HS_Down == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                 if current_time - PublicVarible.last_execution_timeM15 >= 300:  
                     results = send_telegram_messages(f"الگوی سرو شانه نزولی در ناحیه رنج {self.Pair} ", PublicVarible.chat_ids)
                     PublicVarible.HS_Down = 1
                     PublicVarible.last_execution_timeM15 =  time.time()

               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                 if current_time - PublicVarible.last_execution_timeM15 >= 300:  
                     results = send_telegram_messages(f"الگوی سرو شانه صعودی در ناحیه رنج {self.Pair} ", PublicVarible.chat_ids)
                     PublicVarible.HS_Up = 1 
                     PublicVarible.last_execution_timeM15 =  time.time()                  

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.Baseroof5 and close_C < (PublicVarible.Baseroof5 + (SymbolInfo.point * 20)) and PublicVarible.Baseroof5 != 0 :
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C > (PublicVarible.Baseroof5 + (SymbolInfo.point * 20)) and PublicVarible.Baseroof5 != 0 and close_C > higherH : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.Baseroof5} ")
                if current_time - PublicVarible.last_execution_timeS  >= 300:   
                   Text = f"#Buy Position {self.Pair}\n \n"
                   Text += f"price:{close_C}$ 🔺Upper Roof {PublicVarible.Baseroof5}$ \n\n "
                   if trend_C == +1 : 
                       Text += f"خروج قیمت از #سقف با قدرت #زیاد توسط خریداران  🐮 \n "
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                   elif trend_C == +2 : 
                       Text += f"خروج قیمت از #سقف با قدرت #معمولی توسط خریداران 🐮 \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                       PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f" قدرت فروشنده و خریدار #برابر است 🏓 \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f" وضعیت خروج قیمت #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                   #PromptToTelegram(Text)  
                   results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   PublicVarible.last_execution_timeS = current_time 
#Buy
                buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
                if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return
                     
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.Basefloor5 - ((PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2)  #########  تعیین حدضرر معامله ######### - ( SymbolInfo.point * 70)  #
                TP1 =   SymbolInfo.ask + (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 1.2)# SymbolInfo.bid + ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)" 
                write_trade_info_to_file(self.Pair ,"Buy", SymbolInfo.ask, SL, TP1, TextN )

                if (abs(close_C - PublicVarible.Baseroof5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 0.75 )) and (trend_C == +1 ) and Time_Signal == 1 : # and PublicVarible.hmaSignal == 1 :
                  Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  PublicVarible.Exit_C = True
                  EntryPrice = SymbolInfo.ask
                  Entryheight = round(abs(EntryPrice - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                  OrderBuy(Pair= self.Pair, Volume= Volume/2, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")
                
                  EntryPrice = (PublicVarible.Baseroof5 + PublicVarible.Basefloor5)/2
                  #OrderBuyLimit(Pair= self.Pair, Volume= Volume/2 , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")
                  PromptToTelegram(f"🚨🚨 \n سفارش #خرید معوق در قیمت {EntryPrice} گذاشته شد\n LL = {PublicVarible.List_of_low}\n HH = {PublicVarible.List_of_high}")
                  PublicVarible.Limittime = current_time
                else : 
                   TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                   TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)" 
                   write_None(self.Pair , TextN )

                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.Basefloor5 and close_C > (PublicVarible.Basefloor5 - (SymbolInfo.point * 20)) and PublicVarible.Basefloor5 != 0 :
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C < (PublicVarible.Basefloor5 - (SymbolInfo.point * 20)) and PublicVarible.Basefloor5 != 0 and close_C < LowerL : 
                print(f"price is {close_C} and Under floor {PublicVarible.Basefloor5} ")
                if current_time - PublicVarible.last_execution_timeS >= 300:   
                   Text = f"#Sell Position  {self.Pair} \n\n"
                   Text += f"price:{close_C}$ 🔻Under floor {PublicVarible.Basefloor5}$ \n\n "
                   if trend_C == -1 : 
                       Text += f"خروج قیمت از #کف با قدرت #زیاد توسط فروشندگان 🐻 \n"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                   elif trend_C == -2 :
                       Text +=  f"خروج قیمت از #کف با قدرت #معمولی توسط فروشندگان 🐻 \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"الکوی سرشانه نزولی رخ داده است \n "
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"الکوی سرشانه صعودی رخ داده است \n "
                       PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f" قدرت فروشنده و خریدار #برابر است 🏓 \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f" وضعیت خروج قیمت #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                   
                   #PromptToTelegram(Text)
                   results = send_telegram_messages(Text, PublicVarible.chat_ids)  
                   PublicVarible.last_execution_timeS = current_time  
#Sell
                sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
                
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.Baseroof5 + ((PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2) #########  تعیین حدضرر معامله #########  ( SymbolInfo.point * 50 * ATR_Value)  #
                TP1 =  SymbolInfo.bid - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 1.2)  #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Baseroof5) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)\n" 
                write_trade_info_to_file(self.Pair ,"Sell", SymbolInfo.bid  , SL, TP1, TextN )
                
                if (abs(close_C - PublicVarible.Basefloor5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)* 0.75) ) and (trend_C == -1 ) and Time_Signal == 1 : 
                  Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.bid  
                  Entryheight = round(abs(EntryPrice - PublicVarible.Baseroof5) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                  OrderSell(Pair= self.Pair, Volume= Volume/2, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V9 - M5")

                  EntryPrice = (PublicVarible.Baseroof5 + PublicVarible.Basefloor5)/2
                  #OrderSellLimit(Pair= self.Pair, Volume= Volume/2 , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V9 - M5")
                  PromptToTelegram(f"🚨🚨 \n سفارش #فروش معوق در قیمت {EntryPrice} گذاشته شد \n LL = {PublicVarible.List_of_low}\n HH = {PublicVarible.List_of_high}")
                  PublicVarible.Limittime = current_time

                else : 
                    TextN = f"\n self.Pair | pos = Sell | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                

      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500