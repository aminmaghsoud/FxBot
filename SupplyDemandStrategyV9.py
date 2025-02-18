import pandas as PD
from Utility import *
from Trade import *
import time
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
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M5 Range and Spike --")
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
             current_datetime = datetime.now()
             LastCandle = FrameRatesM5.iloc[-1]
             minutes_to_exclude = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
             if (LastCandle['datetime'].hour in [0 , 1 , 8 , 15 , 16, 17])  or PublicVarible.CanOpenOrder == False : #or ((current_datetime.weekday() == 4 and current_datetime.hour > 20)) or (current_datetime.minute not in minutes_to_exclude ) :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                Time_Signal = 0  
             ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
             ATR_Value = ATR.iloc[-1]
             print("ATR_Value" , ATR_Value)
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             current_time = time.time()
             trend_C = 0
             close_C = FrameRatesM5.iloc[-2]['close']
             high_C = FrameRatesM5.iloc[-2]['high'] 
             low_C = FrameRatesM5.iloc[-2]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             if  close_C >= One_third_UP :
                 trend_C = +1
             elif close_C <= One_third_Down :
                 trend_C = -1
             if trend_C == 0 :
                 print("** Mid **")
             elif trend_C == +1 : 
                  print("** One_third_UP **")
             else :  print("** One_third_Down **")
             print("Baseroof5 : " , PublicVarible.Baseroof5)
             print("Close -2 : " , FrameRatesM5.iloc[-2]['close'])
             print("Basefloor5 : " , PublicVarible.Basefloor5)
             

             ## لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Text = None
             if (FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high']) :# and (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low']) : 
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
             if count > 1 : 
                high_low_diff = round((abs( FrameRatesM5['low'].iloc[current_index : -2 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if high_low_diff < (200 * ATR_Value * 0.9) and high_low_diff > (1200 * ATR_Value) : return
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -2 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff * 1000,1) > 50 : return

                PublicVarible.Basefloor5 = FrameRatesM5['low'].iloc[current_index : -2 ].min()
                PublicVarible.Baseroof5 = FrameRatesM5.iloc[-2]['high']
                PublicVarible.range_height = round(abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)
                print(f"Down high_low_diff: {high_low_diff}  and  PublicVarible.Baseroof5: {PublicVarible.Baseroof5}  and  PublicVarible.Basefloor5: {PublicVarible.Basefloor5} and  Range arraye : {abs(PublicVarible.Basefloor5 - PublicVarible.Baseroof5) / (SymbolInfo.point)} \n")
                current_time = time.time()
                if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"سقف: {PublicVarible.Baseroof5} \n"
                   Text += f"کف : {PublicVarible.Basefloor5} \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   Text += f"حجم کل مجاز : {round(Balace * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} \n"
                   Text += f"حجم پله : {round(Balace * (PublicVarible.risk/1000) / PublicVarible.range_height / 3 , 2)} \n"    
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"
                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time = current_time


             ## لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Text = None       
             if (FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low']) :# and (FrameRatesM5.iloc[-2]['high'] < FrameRatesM5.iloc[-3]['high']) :
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
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[current_index : -2]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if high_low_diff < (200 * ATR_Value * 0.9) and high_low_diff > (1200 * ATR_Value) : return
                if round((round(abs((FrameRatesM5.iloc[current_index : -2]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff * 1000,1) > 50 : return

                PublicVarible.Baseroof5 = FrameRatesM5.iloc[current_index : -2]['high'].max()
                PublicVarible.Basefloor5 = FrameRatesM5.iloc[-2]['low']
                PublicVarible.range_height = round(abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)
                print(f"Up high_low_diff: {high_low_diff}  and  PublicVarible.Baseroof5: {PublicVarible.Baseroof5}  and  PublicVarible.Basefloor5: {PublicVarible.Basefloor5} and  Range arraye : {abs(PublicVarible.Basefloor5 - PublicVarible.Baseroof5) / (SymbolInfo.point)} \n")
                current_time = time.time()
                if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"سقف: {PublicVarible.Baseroof5} \n"
                   Text += f"کف : {PublicVarible.Basefloor5} \n"
                   Text += f"نسبت رنج به لگ: {round(PublicVarible.range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {PublicVarible.range_height} pip \n"
                   Text += f"حجم کل مجاز : {round(Balace * (PublicVarible.risk/1000) / PublicVarible.range_height , 2)} \n"
                   Text += f"حجم پله : {round(Balace * (PublicVarible.risk/1000) / PublicVarible.range_height / 3 , 2)} \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"

                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time = current_time
             
             if FrameRatesM5.iloc[-2]['close'] > PublicVarible.Baseroof5 and PublicVarible.Baseroof5 != 0 : 
                print(f"price is {FrameRatesM5.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof5} ")
                if current_time - PublicVarible.last_execution_time >= 300:   
                   Text = f"price is {FrameRatesM5.iloc[-2]['close']} and 🔺Upper #Roof {PublicVarible.Baseroof5} \n "
                   if trend_C == 0 :
                      Text += f" قدرت ها برابر است 🏓"
                   elif trend_C == +1 : 
                       Text += f"قدرت در دست خریداران است 🐮 "
                   else :  Text +=  f"قدرت در دست فروشندگان است 🐻 "
                   PromptToTelegram(Text)  
                   PublicVarible.last_execution_time = current_time 
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
                Entryheight = round(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5) / (SymbolInfo.point) / 10, 2)      
                Volume = round(Balace * (PublicVarible.risk/1000) / Entryheight , 2)                                             ######### قیمت  ورود به معامله ########
                SL = PublicVarible.Basefloor5 - ( SymbolInfo.point * 50) #EntryPrice - round(ATR_Value * 1.5 , 2)  #PublicVarible.Basefloor5 - ( SymbolInfo.point * 50)    #########  تعیین حدضرر معامله #########
                TP1 = abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5) + EntryPrice  #SymbolInfo.bid + ( SymbolInfo.point * 100)   
                write_trade_info_to_file(self.Pair ,"Buy", EntryPrice, SL, TP1, trend_C )
                if (abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Baseroof5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2)) and trend_C == +1 and Time_Signal == 1 : # and PublicVarible.hmaSignal == 1 :
                  Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")
                else : 
                    TextN = f"\n self.Pair | pos = Buy | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} | trend_C = {trend_C} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                  
                  #EntryPrice = PublicVarible.Baseroof5 + ( SymbolInfo.point * 50)
                  #OrderBuyLimit(Pair= self.Pair, Volume= Volume , EntryPrice = EntryPrice , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0  

             if FrameRatesM5.iloc[-2]['close'] < PublicVarible.Basefloor5 and PublicVarible.Basefloor5 != 0 : 
                print(f"price is {FrameRatesM5.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor5} ")
                if current_time - PublicVarible.last_execution_time >= 300:   
                   Text = f"price is {FrameRatesM5.iloc[-2]['close']} and 🔻Under #floor {PublicVarible.Basefloor5} \n "
                   if trend_C == 0 :
                      Text += f" قدرت ها برابر است 🏓"
                   elif trend_C == +1 : 
                       Text += f"قدرت در دست خریداران است 🐮 "
                   else :  Text +=  f"قدرت در دست فروشندگان است 🐻 "
                   PromptToTelegram(Text)  
                   PublicVarible.last_execution_time = current_time  
#Sell
                sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
                
                EntryPrice = SymbolInfo.ask  
                Entryheight = round(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5) / (SymbolInfo.point) / 10, 2)      
                Volume = round(Balace * (PublicVarible.risk/1000) / Entryheight , 2)
                SL = PublicVarible.Baseroof5 + ( SymbolInfo.point * 50) #EntryPrice + round(ATR_Value * 1.5 , 2) #PublicVarible.Baseroof5 + ( SymbolInfo.point * 50)         #########  تعیین حدضرر معامله #########
                TP1 = EntryPrice - abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)  #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                if (abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5) < (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2) ) and trend_C == -1 and Time_Signal == 1 : #and PublicVarible.hmaSignal == -1:
                  Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V2 - M5")
                  write_trade_info_to_file(self.Pair ,"Sell", EntryPrice, SL, TP1, 0 )
                else : 
                    TextN = f"\n self.Pair | pos = Sell | EntryPrice = {EntryPrice} | SL = {SL} | TP1 = {TP1} | trend_C = {trend_C} \n"
                    TextN += f"Time_Signal = {Time_Signal} || trend_C = {trend_C}  ||  Break = {(abs(FrameRatesM5.iloc[-2]['close'] - PublicVarible.Basefloor5)) - (abs(PublicVarible.Baseroof5 - PublicVarible.Basefloor5)/2)} (If NEG T is True)" 
                    write_None(self.Pair , TextN )
                PublicVarible.Baseroof5 = PublicVarible.Basefloor5 = 0
                
      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500