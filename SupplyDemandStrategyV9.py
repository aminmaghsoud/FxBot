import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
from GoldPricePredictor import *
from GoldPricePredictorM5 import *
from GoldPricePredictorM5_XGB import GoldPricePredictorM5_XGB

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

             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 100)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
          
          predicted_change , predicted_changeM5 , predicted_changeXGB = get_signal_from_model(self.Pair)
          
          PairNameX = "دلار امریکا/ اونس طلا"
          Time_Signal = 1
          high_low_diff = 0 
          
          if True :   
             trend5 ,  final_confidence = analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30) 
             print(" trend5: ",trend5 , "final_confidence: " ,round(final_confidence,2) )

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
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
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
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             # دریافت زمان فعلی
             current_time = time.time()
             current_datetime = datetime.now()
             # تعریف بازه‌های زمانی ممنوعه
             restricted_time_ranges = [
                (0, 0, 2, 30),   
                (3,20,3,40), 
                (4,10,4,30),
                (8, 0, 13, 0),  
                (15, 45, 18, 45),  
                (23, 0, 23, 59)   # 22:00 تا 23:59
             ]
             # بررسی اینکه آیا ساعت جاری در یکی از بازه‌های ممنوعه است یا خیر
             in_restricted_time = any(
                start_h * 60 + start_m <= current_datetime.hour * 60 + current_datetime.minute <= end_h * 60 + end_m
                for start_h, start_m, end_h, end_m in restricted_time_ranges
             )

             if in_restricted_time or not PublicVarible.CanOpenOrder or not PublicVarible.Quick_trade :
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
                #PromptToTelegram(f"⚠️ بعلت طولانی شدن زمان باز شدن لیمیت ، سفارش حذف شد!")
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

             #print("PublicVarible.Basetime:",PublicVarible.Basetime)
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
             LowerL = PublicVarible.List_of_low
             higherH = PublicVarible.List_of_high
             #print(f"Lower low = {PublicVarible.List_of_low} \nhigher high = {PublicVarible.List_of_high}")

             if  close_C >= One_third_UP : #and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down : #and close_C < low_C_O :
                 trend_C = -1
            

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
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff * 1000,1) < 60 : 
                 leg_contorol = 400 
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
                   PublicVarible.Leg_trend = -1
                   Text = f"{PairNameX}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴\n\n"
                   #Text += f"تعداد کندل: {count}\n"
                   #Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   #Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   #Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroof5} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloor5} $ \n\n"
                   #Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} Lot \n"
                   #Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}\n"
                   if trend5 == 1 : 
                      Text += f"🔘 پایش قدرت  : قدرت خریدار "
                   elif trend5 == -1 :
                      Text += f"🔘 پایش قدرت  : قدرت فروشنده "
                   elif trend5 == 0 :
                      Text += f"🔘 پایش قدرت  : قدرت ها برابر "
                   Text += f"\n🔘 ضریب اطمینان پایش: {round(final_confidence , 2)}"

                   Text += f" \n\n🔘 آنالیز LR: \n"
                   if predicted_changeM5 >= 0  : 
                      Text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5,1)} $\n"
                   elif predicted_changeM5 < 0  : 
                      Text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5,1)} $\n"
                   if predicted_change >= 0  : 
                      Text += f"رشد بلند مدت :🔺+{round(predicted_change,1)} $\n"
                   elif predicted_change < 0  : 
                      Text += f"رشد بلند مدت :🔻{round(predicted_change,1)} $"
                   Text +=  f" \n🔘 آنالیز XGB  \nرشدکوتاه مدت {round(predicted_changeXGB,2)} $"

                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
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
              if round((round(abs((FrameRatesM5.iloc[current_index : -1]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff * 1000,1) < 60 :
                 leg_contorol = 400 
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
                   PublicVarible.Leg_trend = 1
                   Text = f"{PairNameX}\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n\n"
                   #Text += f"تعداد کندل: {count}\n"
                   #Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   #Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   #Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.Baseroof5} $ \n"
                   Text += f"کف رنج : {PublicVarible.Basefloor5} $ \n\n"
                   #Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} Lot \n"
                   #Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"
                   if trend5 == 1 : 
                      Text += f"🔘 پایش قدرت  : قدرت خریدار "
                   elif trend5 == -1 :
                      Text += f"🔘 پایش قدرت  : قدرت فروشنده "
                   elif trend5 == 0 :
                      Text += f"🔘 پایش قدرت  : قدرت ها برابر "
                   Text += f"\n🔘 ضریب اطمینان پایش: {round(final_confidence , 2)}"

                   Text += f" \n\n🔘 آنالیز LR: \n"
                   if predicted_changeM5 >= 0  : 
                      Text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5,1)} $\n"
                   elif predicted_changeM5 < 0  : 
                      Text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5,1)} $\n"
                   if predicted_change >= 0  : 
                      Text += f"رشد بلند مدت :🔺+{round(predicted_change,1)} $\n"
                   elif predicted_change < 0  : 
                      Text += f"رشد بلند مدت :🔻{round(predicted_change,1)} $"
                   Text +=  f" \n🔘 آنالیز XGB Machine Learning: \nرشدکوتاه مدت {round(predicted_changeXGB,2)} $"

                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
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

#####################  بررسی لگ و جهت روند   ######################
             if PublicVarible.Baseroof5 != 0 :
                return
             elif PublicVarible.Leg_trend == 1  and final_confidence > 0.65 and trend5 == 1 : 
                EntryPrice = SymbolInfo.ask
                SL = FrameRatesM5.iloc[current_index : -1]['low'].min()
                TP1 = EntryPrice + (EntryPrice - SL)
                Volume = 0.0
                OrderBuy(Pair= self.Pair, Volume= Volume , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                OrderBuyLimit(Pair= self.Pair, Volume= Volume   , EntryPrice =  PublicVarible.Basefloor5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                PublicVarible.Limittime = current_time
                PublicVarible.Leg_trend = 0

             elif PublicVarible.Leg_trend == 1  and final_confidence > 0.65 and trend5 == -1 : 
                SL = PublicVarible.Baseroof5  + (PublicVarible.Baseroof5 - PublicVarible.Basefloor5)
                TP1 = PublicVarible.Basefloor5
                Volume = 0.01
                OrderSellLimit(Pair= self.Pair, Volume=  Volume  , EntryPrice =  PublicVarible.Baseroof5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                PublicVarible.Limittime = current_time
                PublicVarible.Leg_trend = 0

             elif PublicVarible.Leg_trend == -1  and final_confidence > 0.65 and trend5 == -1 : 
                EntryPrice = SymbolInfo.bid
                SL = FrameRatesM5.iloc[current_index : -1]['high'].max()
                TP1 = EntryPrice - (SL - EntryPrice )
                Volume = 0.01
                OrderSell(Pair= self.Pair, Volume=  Volume , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                OrderSellLimit(Pair= self.Pair, Volume=  Volume  , EntryPrice =  PublicVarible.Baseroof5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                PublicVarible.Limittime = current_time
                PublicVarible.Leg_trend = 0

             elif PublicVarible.Leg_trend == -1  and final_confidence > 0.65 and trend5 == 1 : 
                SL = PublicVarible.Basefloor5 - ((PublicVarible.Baseroof5 - PublicVarible.Basefloor5))  
                TP1 = PublicVarible.Baseroof5 
                Volume = 0.01
                OrderBuyLimit(Pair= self.Pair, Volume=  Volume  , EntryPrice =  PublicVarible.Basefloor5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Dir11 V9")
                PublicVarible.Limittime = current_time
                PublicVarible.Leg_trend = 0


#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.Baseroof5 and close_C < (PublicVarible.Baseroof5 + (SymbolInfo.point * 1)) and PublicVarible.Baseroof5 != 0 :
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C > (PublicVarible.Baseroof5 + (SymbolInfo.point * 1)) and PublicVarible.Baseroof5 != 0 and close_C > higherH : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.Baseroof5} ")
                if current_time - PublicVarible.last_execution_timeS  >= 300:   
                   Text = f"\n({PairNameX}) \n⬆️ Buy Position in {self.Pair} \n"
                   Text += f"price:{close_C}$ \n🔺Upper Roof {PublicVarible.Baseroof5}$ \n\n"
                   if trend_C == +1 : 
                       Text += f"🔘خروج  از سقف:  کندل قدرتمند 🐮 \n"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == +2 : 
                       Text += f"🔘 خروج از سقف:  کندل قدرتمند 🐮 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f"🔘 قدرت کندل ها : شناسایی نشد  🏓 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f"🔘 وضعیت خروج : نامناسب  \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                   
                   if trend5 == 1 : 
                      Text += f"🔘 پایش قدرت  : قدرت خریدار "
                   elif trend5 == -1 :
                      Text += f"🔘 پایش قدرت  : قدرت فروشنده "
                   elif trend5 == 0 :
                      Text += f"🔘 پایش قدرت  : قدرت ها برابر "
                   if final_confidence < 65 :
                     Text += f"\n🔘 ضریب اطمینان پایش مناسب نیست ⚠️({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
                   if trend_C == +1 and trend5 == 1 and final_confidence > 65 : 
                      Text += f"\n✅ موقعیت Buy: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Buy: نامناسب "

                   Text += f" \n\n🔘 آنالیز LR: \n"
                   if predicted_changeM5 >= 0  : 
                      Text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5,1)} $\n"
                   elif predicted_changeM5 < 0  : 
                      Text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5,1)} $\n"
                   if predicted_change >= 0  : 
                      Text += f"رشد بلند مدت :🔺+{round(predicted_change,1)} $\n"
                   elif predicted_change < 0  : 
                      Text += f"رشد بلند مدت :🔻{round(predicted_change,1)} $"
                   Text +=  f" \n🔘 آنالیز XGB Machine Learning: \nرشدکوتاه مدت {round(predicted_changeXGB,2)} $"

                   #PromptToTelegram(Text)  
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   #results = send_telegram_messages(Text, PublicVarible.chat_ids)
                   PublicVarible.last_execution_timeS = current_time 
#Buy
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.Basefloor5 - ((PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)  #########  تعیین حدضرر معامله ######### - ( SymbolInfo.point * 70)  #
                TP1 = PublicVarible.Baseroof5 + (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 2) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)" 
                write_trade_info_to_file(self.Pair ,"Buy", SymbolInfo.ask, SL, TP1, TextN )

                if (abs(close_C - PublicVarible.Baseroof5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 0.75 )) and trend_C == +1  and trend5== 1 and final_confidence > 65 and Time_Signal == 1 :
                  Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.ask
                  Entryheight = round(abs(EntryPrice - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                  ### سفارش خرید در قیمت مارکت   ############
                  OrderBuy(Pair= self.Pair, Volume= round(Volume/2 ,2) , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Mar V9")
                  ### سفارش خرید در قیمت کف رنج   ############
                  OrderBuyLimit(Pair= self.Pair, Volume=  round(Volume/2 ,2)  , EntryPrice =  PublicVarible.Basefloor5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim V9")
                  #PromptToTelegram(f"🚨🚨 \n سفارش #خرید معوق {self.Pair} در قیمت \n SL : {SL} \n Price : {EntryPrice} \n TP : {TP1}")
                  PublicVarible.Limittime = current_time
                else : 
                   TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                   TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)" 
                   write_None(self.Pair , TextN )

                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.Basefloor5 and close_C > (PublicVarible.Basefloor5 - (SymbolInfo.point * 1)) and PublicVarible.Basefloor5 != 0 :
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک شدن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C < (PublicVarible.Basefloor5 - (SymbolInfo.point * 1)) and PublicVarible.Basefloor5 != 0 and close_C < LowerL : 
                print(f"price is {close_C} and Under floor {PublicVarible.Basefloor5} ")
                if current_time - PublicVarible.last_execution_timeS >= 300:   
                   Text = f"\n({PairNameX}) \n⬇️ Sell Position in {self.Pair} \n"
                   Text += f"🔘price:{close_C}$ \n🔻Under floor {PublicVarible.Basefloor5}$ \n\n"
                   if trend_C == -1 : 
                       Text += f"🔘 خروج از کف: باکندل قدرتمند 🐻 \n"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"🔘الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == -2 :
                       Text +=  f"🔘خروج از کف: باکندل معولی 🐻 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_Down == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_Up == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                   elif trend_C == 0 :
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f"🔘 قدرت کندل ها برابر  🏓 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                      Text += f"🔘 وضعیت خروج:  نامناسب  \n🔘حذف مقادیر سقف و کف ⚠️\n"
                   if trend5 == 1 : 
                      Text += f"🔘 پایش قدرت  : قدرت خریدار "
                   elif trend5 == -1 :
                      Text += f"🔘 پایش قدرت  : قدرت فروشنده "
                   elif trend5 == 0 :
                      Text += f"🔘 پایش قدرت  : قدرت ها برابر "
                   if final_confidence < 65 : 
                     Text += f"\n🔘 ضریب اطمینان پایش مناسب نیست ⚠️({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
                   
                   if trend_C == -1 and trend5 == -1 and final_confidence > 65 : 
                      Text += f"\n✅ موقعیت Sell: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Sell: نامناسب "

                   Text += f" \n\n🔘 آنالیز LR: \n"
                   if predicted_changeM5 >= 0  : 
                      Text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5,1)} $\n"
                   elif predicted_changeM5 < 0  : 
                      Text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5,1)} $\n"
                   if predicted_change >= 0  : 
                      Text += f"رشد بلند مدت :🔺+{round(predicted_change,1)} $\n"
                   elif predicted_change < 0  : 
                      Text += f"رشد بلند مدت :🔻{round(predicted_change,1)} $"
                   Text +=  f" \n🔘 آنالیز XGB Machine Learning: \nرشدکوتاه مدت {round(predicted_changeXGB,2)} $"

                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeS = current_time  
#Sell
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.Baseroof5 + ((PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75) #########  تعیین حدضرر معامله #########  ( SymbolInfo.point * 50 * ATR_Value)  #
                TP1 = PublicVarible.Basefloor5 - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) * 2) 
                Entryheight = round(abs(EntryPrice - PublicVarible.Baseroof5) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)*0.75)} (If NEG T is True)\n" 
                write_trade_info_to_file(self.Pair ,"Sell", SymbolInfo.bid  , SL, TP1, TextN )
                
                if (abs(close_C - PublicVarible.Basefloor5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)* 0.75) ) and trend_C == -1  and trend5 == -1  and final_confidence > 65 and Time_Signal == 1 : 
                  EntryPrice = SymbolInfo.bid  
                  Entryheight = round(abs(EntryPrice - PublicVarible.Baseroof5) / (SymbolInfo.point) / 10, 2)      
                  Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)/2
                  ### سفارش خرید در قیمت مارکت   ############
                  OrderSell(Pair= self.Pair, Volume= round(Volume/2 ,2)  , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "Mar V9")
                  Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  ### سفارش خرید در قیمت کف رنج   ############
                  OrderSellLimit(Pair= self.Pair, Volume=  round(Volume/2 ,2) , EntryPrice =  PublicVarible.Baseroof5 , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim V9")
                  #PromptToTelegram(f"🚨🚨 \n سفارش #فروش معوق {self.Pair} در قیمت \n SL : {SL} \n Price : {PublicVarible.Baseroof5} \n TP : {TP1}")
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