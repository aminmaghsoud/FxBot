import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV6():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair !='BTCUSD' : return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V6 M5  ")
          # ارسال پیام
          
          Time_Signal = 1
          high_low_diff = 0 
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

             trendB ,  final_confidence = analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30) 
             print("trendB: ",trendB , "final_confidence: " ,final_confidence )

             PairNameB = "بیتکوین/دلار امریکا"
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

             if in_restricted_time or not PublicVarible.CanOpenOrder  or not PublicVarible.Quick_trade :
                 Botdashboard(4, self.Pair)
                 Time_Signal = 0

             #ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
             #ATR_Value = ATR.iloc[-1]
             #print("ATR_Value" , ATR_Value)
             ATR_Value = 1
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             if current_time - PublicVarible.BasetimeB >= 2100 and PublicVarible.BasetimeB != 0 and PublicVarible.BasefloorB != 0: 
                PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0  
                PublicVarible.BasetimeB = 0

             if current_time - PublicVarible.Limittime >= 900 and PublicVarible.Limittime != 0 : 
               delete_all_limit_orders()  
                #PromptToTelegram(f"⚠️ بعلت طولانی کردن زمان باز کردن لیمیت ، سفارش حذف شد!")
               PublicVarible.Limittime = 0

             #print("PublicVarible.BasetimeB:",PublicVarible.BasetimeB)
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
             LowerLB = PublicVarible.LowerLB
             HigherHB = PublicVarible.HigherHB
             print(f"Lower low = {PublicVarible.LowerLB} \nhigher high = {PublicVarible.HigherHB}")

             if  close_C >= One_third_UP :# and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down :# and close_C < low_C_O :
                 trend_C = -1
             #elif close_C > One_third_Down and close_C < One_third_UP :# and close_C > high_C_O :
             #    trend_C = +2
             #elif close_C > One_third_Down and close_C < One_third_UP :# and  close_C < low_C_O :
             #    trend_C = -2
                 
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

             print(f"\n BaseroofB : {PublicVarible.BaseroofB}")
             print("Close -2 : " , close_C)
             print("BasefloorB : " , PublicVarible.BasefloorB)
             

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
                  PublicVarible.HigherHB = high_C 
                  PublicVarible.LowerLB = low_C 
                  PublicVarible.BasefloorB = FrameRatesM5['low'].iloc[current_index : -1 ].min()
                  PublicVarible.BaseroofB = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.BasetimeB = current_time
                  PublicVarible.range_heightB = round(abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB) / (SymbolInfo.point) / 10, 2)
                  print(f"Down high_low_diff: {high_low_diff} and BaseroofB: {PublicVarible.BaseroofB} and BasefloorB: {PublicVarible.BasefloorB} and Range arraye: {abs(PublicVarible.BasefloorB - PublicVarible.BaseroofB) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if round(PublicVarible.range_heightB / high_low_diff * 1000,1) > 50 :
                     PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                  elif current_time - PublicVarible.last_execution_timeB >= 300:  
                   Text = f"{PairNameB}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightB} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightB / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.BaseroofB} $ \n"
                   Text += f"کف رنج : {PublicVarible.BasefloorB} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightB , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}\n"
                   if trendB == 1 : 
                      Text += f"🔘 پایش قدرت : قدرت خریدار "
                   elif trendB == -1 :
                      Text += f"🔘 پایش قدرت :قدرت فروشنده "
                   elif trendB == 0 :
                      Text += f"🔘 پایش قدرت : قدرت ها برابر "
                   if final_confidence < 0.65 : 
                     Text += f"\n⚠️ ضریب اطمینان پایش مناسب نیست ({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeB = current_time


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
                  PublicVarible.HigherHB = high_C 
                  PublicVarible.LowerLB = low_C  
                  PublicVarible.BaseroofB = FrameRatesM5.iloc[current_index : -1]['high'].max()
                  PublicVarible.BasefloorB = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.BasetimeB = current_time
                  PublicVarible.range_heightB = round(abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB) / (SymbolInfo.point) / 10, 2)
                  print(f"Up high_low_diff: {high_low_diff} and BaseroofB: {PublicVarible.BaseroofB} and BasefloorB: {PublicVarible.BasefloorB} and Range arraye: {abs(PublicVarible.BasefloorB - PublicVarible.BaseroofB) / (SymbolInfo.point)} \n")
                  current_time = time.time()
                  if round(PublicVarible.range_heightB / high_low_diff * 1000,1) > 50 :
                     PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                  elif current_time - PublicVarible.last_execution_timeB >= 300:  
                   Text = f"{PairNameB}\n"
                   Text += f"{self.Pair} Price is ({SymbolInfo.ask} $)\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_heightB} pip \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_heightB / high_low_diff * 1000,1) } % \n"
                   Text += f"سقف رنج: {PublicVarible.BaseroofB} $ \n"
                   Text += f"کف رنج : {PublicVarible.BasefloorB} $ \n"
                   Text += f"حجم کل مجاز : {round((Balace * 0.8) * (PublicVarible.risk/1000) / PublicVarible.range_heightB , 2)} Lot \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"
                   if trendB == 1 : 
                      Text += f"🔘 پایش قدرت : قدرت خریدار "
                   elif trendB == -1 :
                      Text += f"🔘 پایش قدرت :قدرت فروشنده "
                   elif trendB == 0 :
                      Text += f"🔘 پایش قدرت : قدرت ها برابر "
                   if final_confidence < 0.65 : 
                     Text += f"\n⚠️ ضریب اطمینان پایش مناسب نیست ({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeB = current_time

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.BaseroofB != 0 and close_C < PublicVarible.BaseroofB and close_C > PublicVarible.BasefloorB : 
               if high_C > PublicVarible.HigherHB : 
                  PublicVarible.HigherHB = high_C 
               if low_C < PublicVarible.LowerLB: 
                  PublicVarible.LowerLB = low_C
             elif PublicVarible.BasefloorB == 0 : 
                  PublicVarible.LowerLB = PublicVarible.HigherHB  = 0

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

             if PublicVarible.BasefloorB == 0 : PublicVarible.HS_UpB = PublicVarible.HS_DownB = 0 
             elif PublicVarible.BasefloorB != 0 and PublicVarible.HS_UpB == 0 and PublicVarible.HS_DownB == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                     PublicVarible.HS_DownB = 1
               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                     PublicVarible.HS_UpB = 1 

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.BaseroofB and close_C < (PublicVarible.BaseroofB + (SymbolInfo.point * 1)) and PublicVarible.BaseroofB != 0 :
                PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C >= (PublicVarible.BaseroofB + (SymbolInfo.point * 1)) and PublicVarible.BaseroofB != 0 and close_C > HigherHB : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.BaseroofB} ")
                if current_time - PublicVarible.last_execution_timeBS  >= 300:   
                   Text = f"\n({PairNameB}) \n⬆️ Buy Position in {self.Pair} \n"
                   Text += f"price:{close_C}$ \n🔺Upper Roof {PublicVarible.BaseroofB}$ \n\n"
                   if trend_C == +1 : 
                       Text += f"🔘خروج  از سقف:  کندل قدرتمند 🐮 \n"
                       if PublicVarible.HS_DownB == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpB == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == +2 : 
                       Text += f"🔘 خروج از سقف:  کندل قدرتمند 🐮 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_DownB == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpB == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                      Text += f"🔘 قدرت کندل ها : شناسایی نشد  🏓 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                      Text += f"🔘 وضعیت خروج : نامناسب  \n🔘 حذف مقادیر سقف و کف ⚠️\n"
                   if trendB == 1 : 
                      Text += f"🔘 پایش قدرت : قدرت خریدار "
                   elif trendB == -1 :
                      Text += f"🔘 پایش قدرت :قدرت فروشنده "
                   elif trendB == 0 :
                      Text += f"🔘 پایش قدرت : قدرت ها برابر "
                   if final_confidence < 0.65 : 
                     Text += f"\n⚠️ ضریب اطمینان پایش مناسب نیست ({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
                   if trendB == 1 and trend_C == 1 : 
                      Text += f"\n✅ موقعیت Buy: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Buy: نامناسب "
                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeBS = current_time 
#Buy
                
                     
                EntryPrice = SymbolInfo.ask
                SL = PublicVarible.BasefloorB - ( SymbolInfo.point * 70)  #((PublicVarible.BaseroofB - PublicVarible.BasefloorB)/2)  #########  تعیین حدضرر معامله #########
                TP1 =  PublicVarible.BaseroofB + (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*2)# SymbolInfo.bid + ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorB) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BaseroofB)) - (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*0.75)} (If NEG T is True)" 
                write_trade_info_to_file(self.Pair ,"Buy", SymbolInfo.ask, SL, TP1, TextN )

                if (abs(close_C - PublicVarible.BaseroofB) < (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB) * 0.75 )) and (trend_C == +1 ) and trendB == 1 and Time_Signal == 1 : # and PublicVarible.hmaSignal == 1 :
                  Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.ask
                  Entryheight = round(abs(EntryPrice - PublicVarible.BasefloorB) / (SymbolInfo.point) / 10, 2)      
                  Volume = 0.01 # round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2) 
                  #OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V8 AUD ")
                  EntryPrice = (PublicVarible.BaseroofB + PublicVarible.BasefloorB)/2
                  OrderBuyLimit(Pair= self.Pair, Volume= Volume , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim  V6")
                  #PromptToTelegram(f"🚨🚨 \n سفارش #خرید معوق در قیمت \n TP : {TP1} \n Price : {EntryPrice} \n SL : {SL}")
                  PublicVarible.Limittime = current_time
                else : 
                   TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                   TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BaseroofB)) - (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*0.75)} (If NEG T is True)" 
                   write_None(self.Pair , TextN )

                PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.BasefloorB and close_C > (PublicVarible.BasefloorB + (SymbolInfo.point * 5)) and PublicVarible.BasefloorB != 0 :
                PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C <= (PublicVarible.BasefloorB - (SymbolInfo.point * 1)) and PublicVarible.BasefloorB != 0 and close_C < LowerLB : 
                print(f"price is {close_C} and Under floor {PublicVarible.BasefloorB} ")
                if current_time - PublicVarible.last_execution_timeBS >= 300:   
                   Text = f"\n({PairNameB}) \n⬇️ Sell Position in {self.Pair} \n"
                   Text += f"🔘price:{close_C}$ \n🔻Under floor {PublicVarible.BasefloorB}$ \n\n"
                   if trend_C == -1 : 
                       Text += f"🔘 خروج از کف: باکندل قدرتمند 🐻 \n"
                       if PublicVarible.HS_DownB == 1 : 
                          Text += f"🔘الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpB == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                   elif trend_C == -2 :
                       Text +=  f"🔘خروج از کف: باکندل معولی 🐻 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                       if PublicVarible.HS_DownB == 1 : 
                          Text += f"🔘 الگوی سر وشانه نزولی \n"
                       elif PublicVarible.HS_UpB == 1 : 
                          Text += f"🔘 الگوی سر وشانه صعودی \n"
                       PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                      Text += f"🔘 قدرت کندل ها برابر  🏓 \n🔘حذف مقادیر سقف و کف ⚠️\n"
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0
                      Text += f"🔘 وضعیت خروج:  نامناسب  \n🔘حذف مقادیر سقف و کف ⚠️\n"
                   if trendB == 1 : 
                      Text += f"🔘 پایش قدرت : قدرت خریدار "
                   elif trendB == -1 :
                      Text += f"🔘 پایش قدرت :قدرت فروشنده "
                   elif trendB == 0 :
                      Text += f"🔘 پایش قدرت : قدرت ها برابر "
                   if final_confidence < 0.65 : 
                     Text += f"\n⚠️ ضریب اطمینان پایش مناسب نیست ({round(final_confidence , 2)}) "
                   else :
                     Text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "  
                   if trendB == -1 and trend_C == -1 : 
                      Text += f"\n✅ موقعیت Sell: مناسب "
                   else : 
                      Text += f"\n❌ موقعیت Sell: نامناسب "

                   plot_candles_and_send_telegram(FrameRatesM5, self.Pair, Text)
                   PublicVarible.last_execution_timeBS = current_time  
#Sell
                
                
                EntryPrice = SymbolInfo.bid 
                SL = PublicVarible.BaseroofB + ( SymbolInfo.point * 70)  #((PublicVarible.BaseroofB - PublicVarible.BasefloorB)/2) #########  تعیین حدضرر معامله #########
                TP1 = PublicVarible.BasefloorB - (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*2)  #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofB) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                TextN = f"\nVolume = {Volume} \n"
                TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BasefloorB)) - (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*0.75)} (If NEG T is True)\n" 
                write_trade_info_to_file(self.Pair ,"Sell", SymbolInfo.bid  , SL, TP1, TextN )
                
                if (abs(close_C - PublicVarible.BasefloorB) < (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)* 0.75) ) and (trend_C == -1 ) and trendB == -1 and Time_Signal == 1 : #and PublicVarible.hmaSignal == -1:
                  Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  EntryPrice = SymbolInfo.bid  
                  Entryheight = round(abs(EntryPrice - PublicVarible.BaseroofB) / (SymbolInfo.point) / 10, 2)      
                  Volume = 0.01 # round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)
                  #OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V7 AUD")
                  EntryPrice = (PublicVarible.BaseroofB + PublicVarible.BasefloorB)/2
                  OrderSellLimit(Pair= self.Pair, Volume= Volume , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Lim  V6")
                  #PromptToTelegram(f"🚨🚨 \n سفارش #فروش معوق در قیمت \n SL : {SL} \n Price : {EntryPrice} \n TP : {TP1}")
                  PublicVarible.Limittime = current_time

                else : 
                    TextN = f"\n self.Pair | pos = Sell | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.BasefloorB)) - (abs(PublicVarible.BaseroofB - PublicVarible.BasefloorB)*0.75)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                PublicVarible.BaseroofB = PublicVarible.BasefloorB = 0

                

      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500