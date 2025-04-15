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

class SupplyDemandStrategyV8():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair !='USDJPYb' : return 

          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V8 M5  ")
          # ارسال پیام
          Time_Signal = 1
          #PublicVarible.high_low_diffj  = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 100)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
          
             trendj = analyze_market_power(FrameRatesM5) 
             PairNameJ = "ین ژاپن/دلار امریکا"
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
                                 elif SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.65 + entry_price):
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
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.65 - entry_price):
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
                (0, 0, 1, 30),    
                (8, 0, 9, 0),  
                #(15, 45, 18, 45),  
                (23, 0, 23, 59) 
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
             if current_time - PublicVarible.Basetimej >= 2100 and PublicVarible.Basetimej != 0 and PublicVarible.Basefloorj != 0: 
                PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0  
                #PromptToTelegram(f"⚠️ بعلت طولانی شدن خروج قیمت از ناحیه رنج ، ناحیه حذف شد!")
                PublicVarible.Basetimej = 0

             has_pending = has_pending_limit_orders()
             if  has_pending and  current_time - PublicVarible.Limittime >= 1500  : 
                delete_all_limit_orders()  
                # PromptToTelegram(f"⚠️ بعلت طولانی شدن زمان باز کردن لیمیت ، سفارش حذف شد!")
                PublicVarible.Limittime = 0


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
                     

             #print("PublicVarible.Basetimej:",PublicVarible.Basetimej)
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
             LowerLj = PublicVarible.LowerLj
             HigherHj = PublicVarible.HigherHj
             #print(f"Lower low = {PublicVarible.LowerLj} \nhigher high = {PublicVarible.HigherHj}")

             if  close_C >= One_third_UP : #and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down : # and close_C < low_C_O :
                 trend_C = -1
            
             print(f"\n Baseroofj : {PublicVarible.Baseroofj}")
             print("Close -2 : " , close_C)
             print("Basefloorj : " , PublicVarible.Basefloorj)
             

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
                PublicVarible.Leg_startj = FrameRatesM5.iloc[current_index]['high']
                PublicVarible.high_low_diffj  = round((abs( FrameRatesM5['low'].iloc[current_index : -1 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point) / 10, 2) / PublicVarible.high_low_diffj  * 1000,1) < 60 : 
                 leg_contorol = 150
                 if PublicVarible.high_low_diffj  > (leg_contorol) and PublicVarible.high_low_diffj  < (1200 * ATR_Value) : 
                  PublicVarible.HigherHj = high_C 
                  PublicVarible.LowerLj = low_C 
                  PublicVarible.Basefloorj = FrameRatesM5['low'].iloc[current_index : -1 ].min() 
                  PublicVarible.Baseroofj = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.Basetimej = current_time
                  PublicVarible.range_heightj = round(abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj) / (SymbolInfo.point) / 10, 2)
                  print(f"Down PublicVarible.high_low_diffj : {PublicVarible.high_low_diffj } and Baseroofj: {PublicVarible.Baseroofj} and Basefloorj: {PublicVarible.Basefloorj} and Range arraye: {abs(PublicVarible.Basefloorj - PublicVarible.Baseroofj) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if current_time - PublicVarible.last_execution_timej >= 300:  
                   Text = f"{PairNameJ}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(PublicVarible.high_low_diffj , 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightj} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightj / PublicVarible.high_low_diffj  * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroofj} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloorj} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightj , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}\n"
                   trendj = analyze_market_power(FrameRatesM5) 
                   if trendj == 1 : 
                      Text += f"🔘 آنالیز چندگانه : قدرت با خریداران "
                   elif trendj == -1 :
                      Text += f"🔘 آنالیز چندگانه : قدرت با فروشندگان "
                   elif trendj == 0 :
                      Text += f"🔘 آنالیز چندگانه : قدرت ها برابر "
                   #PromptToTelegram(Text)
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   # ارسال نمودار کندل‌ها
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timej = current_time


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
              PublicVarible.Leg_startj = FrameRatesM5.iloc[current_index]['low']
              PublicVarible.high_low_diffj  = round((abs(FrameRatesM5.iloc[current_index : -1]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
              if  round((round(abs((FrameRatesM5.iloc[current_index : -1]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / PublicVarible.high_low_diffj * 1000,1) < 60 :
                 leg_contorol = 150
                 if PublicVarible.high_low_diffj  > (leg_contorol) and PublicVarible.high_low_diffj  < (1200 * ATR_Value) : 
                  PublicVarible.HigherHj = high_C 
                  PublicVarible.LowerLj = low_C  
                  PublicVarible.Baseroofj = FrameRatesM5.iloc[current_index : -1]['high'].max()
                  PublicVarible.Basefloorj = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.Basetimej = current_time
                  PublicVarible.range_heightj = round(abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj) / (SymbolInfo.point) / 10, 2)
                  print(f"Up PublicVarible.high_low_diffj : {PublicVarible.high_low_diffj } and Baseroofj: {PublicVarible.Baseroofj} and Basefloorj: {PublicVarible.Basefloorj} and Range arraye: {abs(PublicVarible.Basefloorj - PublicVarible.Baseroofj) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  
                  if current_time - PublicVarible.last_execution_timej >= 300:  
                   Text = f"{PairNameJ}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(PublicVarible.high_low_diffj , 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightj} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightj / PublicVarible.high_low_diffj  * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroofj} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloorj} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightj , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"
                   trendj = analyze_market_power(FrameRatesM5) 
                   if trendj == 1 : 
                      Text += f"🔘 آنالیز چندگانه : قدرت با خریداران "
                   elif trendj == -1 :
                      Text += f"🔘 آنالیز چندگانه : قدرت با فروشندگان "
                   elif trendj == 0 :
                      Text += f"🔘 آنالیز چندگانه : قدرت ها برابر "
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   #PromptToTelegram(Text)
                   # ارسال نمودار کندل‌ها
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timej = current_time

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.Baseroofj != 0 and close_C < PublicVarible.Baseroofj and close_C > PublicVarible.Basefloorj : 
               if high_C > PublicVarible.HigherHj : 
                  PublicVarible.HigherHj = high_C 
               if low_C < PublicVarible.LowerLj: 
                  PublicVarible.LowerLj = low_C
             elif PublicVarible.Basefloorj == 0 : 
                  PublicVarible.LowerLj = PublicVarible.HigherHj  = 0

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

             if PublicVarible.Basefloorj == 0 : PublicVarible.HS_UpJ = PublicVarible.HS_DownJ = 0 
             elif PublicVarible.Basefloorj != 0 and PublicVarible.HS_UpJ == 0 and PublicVarible.HS_DownJ == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                     PublicVarible.HS_DownJ = 1
               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                     PublicVarible.HS_UpJ = 1 

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.Baseroofj and close_C < (PublicVarible.Baseroofj + (SymbolInfo.point * 5)) and PublicVarible.Baseroofj != 0 :
                PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n 🔘 حذف مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C >= (PublicVarible.Baseroofj + (SymbolInfo.point * 1)) and PublicVarible.Baseroofj != 0 and close_C > HigherHj : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.Baseroofj} ")
                if current_time - PublicVarible.last_execution_timejS  >= 300:   
                   Text = f"\n⬆️ Buy Position in {self.Pair} \n({PairNameJ}) \n"
                   Text += f"price:{close_C}$ \n🔺Upper Roof {PublicVarible.Baseroofj}$ \n\n"
                   if trend_C == +1 : 
                       Text += f"🔘خروج  از سقف:  کندل قدرتمند 🐮 \n"
                       if PublicVarible.HS_DownJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == +2 : 
                       Text += f"🔘 خروج از سقف:  کندل قدرتمند 🐮 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_DownJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                      Text += f"🔘 قدرت کندل ها : برابر  🏓 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                      Text += f"🔘 وضعیت خروج : نامناسب  \n🔘 حذف مقادیر سقف و کف ⚠️\n"

                   trendj = analyze_market_power(FrameRatesM5) 
                   if trendj == 1 : 
                      Text += f"🔘 آنالیز چندگانه : قدرت با خریداران "
                   elif trendj == -1 :
                      Text += f"🔘 آنالیز چندگانه : قدرت با فروشندگان "
                   elif trendj == 0 :
                      Text += f"🔘 آنالیز چندگانه : قدرت ها برابر "
                   if trend_C == 1 and trendj == 1 : 
                      Text += f"\n✅ موقعیت Buy: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Buy: نامناسب "
                   #PromptToTelegram(Text)  
                  # results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timejS = current_time 
#Buy            
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.Basefloorj - ( SymbolInfo.point * 100)  #########  تعیین حدضرر معامله #########
                #TP1 = EntryPrice + ((EntryPrice - SL) * 1  )
                TP1 =  PublicVarible.Baseroofj + (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj) * 1) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Basefloorj) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroofj)) - (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj)*0.75)} (If NEG T is True)" 
                write_trade_info_to_file(self.Pair ,"Buy", SymbolInfo.ask, SL, TP1, TextN )

                if  trend_C == +1 and trendj == +1 and Time_Signal == 1  : 
                   if  (abs(close_C - PublicVarible.Baseroofj) < (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj) * 0.75 )):       
                     Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                     EntryPrice = SymbolInfo.ask
                     Entryheight = round(abs(EntryPrice - PublicVarible.Basefloorj) / (SymbolInfo.point) / 10, 2)      
                     Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                     ### سفارش خرید در قیمت مارکت  ############
                     OrderBuy(Pair= self.Pair, Volume= round(Volume/2 ,2)  , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Mar V8")
                     ### سفارش خرید در قیمت سقف رنج   ############
                     OrderBuyLimit(Pair= self.Pair, Volume= round(Volume/2 ,2) , EntryPrice =  PublicVarible.Basefloorj , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim V8")
                     #PromptToTelegram(f"🚨🚨 \n سفارش #خرید معوق {self.Pair} در قیمت \n TP : {TP1} \n Price : {EntryPrice} \n SL : {SL}")
                     PublicVarible.Limittime = current_time
                     
                else : 
                   TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                   TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroofj)) - (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj)*0.75)} (If NEG T is True)" 
                   write_None(self.Pair , TextN )

                PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.Basefloorj and close_C > (PublicVarible.Basefloorj + (SymbolInfo.point * 2)) and PublicVarible.Basefloorj != 0 :
                PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n 🔘 حذف مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C <= (PublicVarible.Basefloorj - (SymbolInfo.point * 5)) and PublicVarible.Basefloorj != 0 and close_C < LowerLj : 
                print(f"price is {close_C} and Under floor {PublicVarible.Basefloorj} ")
                if current_time - PublicVarible.last_execution_timejS >= 300:   
                   Text = f"\n⬇️ Sell Position in {self.Pair} \n({PairNameJ}) \n"
                   Text += f"🔘price:{close_C}$ \n🔻Under floor {PublicVarible.Basefloorj}$ \n\n"
                   if trend_C == -1 : 
                       Text += f"🔘 خروج از کف: باکندل قدرتمند 🐻 \n"
                       if PublicVarible.HS_DownJ == 1 : 
                          Text += f"🔘الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == -2 :
                       Text +=  f"🔘خروج از کف: باکندل معولی 🐻 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_DownJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpJ == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                      Text += f"🔘 قدرت کندل ها برابر  🏓 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0
                      Text += f"🔘 وضعیت خروج:  نامناسب  \n🔘حذف مقادیر سقف و کف ⚠️\n"
                  
                   trendj = analyze_market_power(FrameRatesM5) 
                   if trendj == 1 : 
                      Text += f"🔘 آنالیز چندگانه : قدرت با خریداران "
                   elif trendj == -1 :
                      Text += f"🔘 آنالیز چندگانه : قدرت با فروشندگان "
                   elif trendj == 0 :
                      Text += f"🔘 آنالیز چندگانه : قدرت ها برابر "
                   if trend_C == -1 and trendj == -1 : 
                      Text += f"\n✅ موقعیت Sell: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Sell: نامناسب "

                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   #PromptToTelegram(Text)
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)  
                   PublicVarible.last_execution_timejS = current_time  
#Sell
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.Baseroofj + ( SymbolInfo.point * 100)  #((PublicVarible.Baseroofj - PublicVarible.Basefloorj)/2)                     #########  تعیین حدضرر معامله #########
                   #TP1 = EntryPrice + ((EntryPrice - SL) * 1  )
                TP1 = PublicVarible.Basefloorj- (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj) * 2) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Baseroofj) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloorj)) - (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj)*0.75)} (If NEG T is True)\n" 
                write_trade_info_to_file(self.Pair ,"Sell", SymbolInfo.bid  , SL, TP1, TextN )
                
                if  trend_C == -1  and trendj == -1 and Time_Signal == 1 :
                   if  (abs(close_C - PublicVarible.Basefloorj) < (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj)* 0.75) ) :
                     Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                     EntryPrice = SymbolInfo.bid  
                     Entryheight = round(abs(EntryPrice - PublicVarible.Baseroofj) / (SymbolInfo.point) / 10, 2)      
                     Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                     ### سفارش خرید در قیمت مارکت   ############
                     OrderSell(Pair= self.Pair, Volume= round(Volume/2 ,2), StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "Mar V8")
                     ### سفارش خرید در قیمت کف رنج   ############
                     OrderSellLimit(Pair= self.Pair, Volume=  round(Volume/2 ,2) , EntryPrice =  PublicVarible.Baseroofj , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim V8")
                     #PromptToTelegram(f"🚨🚨 \n سفارش #فروش معوق {self.Pair} در قیمت \n SL : {SL} \n Price : {EntryPrice} \n TP : {TP1}")
                     PublicVarible.Limittime = current_time

                else : 
                    TextN = f"\n self.Pair | pos = Sell | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloorj)) - (abs(PublicVarible.Baseroofj - PublicVarible.Basefloorj)*0.75)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                PublicVarible.Baseroofj = PublicVarible.Basefloorj = 0

                

      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500