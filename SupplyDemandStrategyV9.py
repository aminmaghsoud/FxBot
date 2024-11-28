import pandas as PD
from Utility import *
from Trade import *
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style

class SupplyDemandStrategyV9():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M5 Range and Spike --")
          
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
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.50 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = entry_price
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             current_datetime = datetime.now()
             LastCandle = FrameRatesM5.iloc[-1]
             minutes_to_exclude = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
             if (LastCandle['datetime'].hour in [0 , 1]) or ((current_datetime.weekday() == 4 and current_datetime.hour > 20)) or (current_datetime.minute not in minutes_to_exclude ) :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return 
             ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
             ATR_Value = ATR.iloc[-1]
             print("ATR_Value" , ATR_Value)
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             ## لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
            
             Text = None
             current_time = time.time()

             if (FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high']) : #or (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low']) : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H : #and Now_c_L < Old_c_L :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
             if count > 1 : 
                high_low_diff = round((abs( FrameRatesM5['low'].iloc[current_index : -2 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if high_low_diff < (200 * ATR_Value * 0.9) : return
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -2 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff * 1000,1) > 50 : return

                PublicVarible.Basefloor = FrameRatesM5['low'].iloc[current_index : -2 ].min()
                PublicVarible.Baseroof = FrameRatesM5.iloc[-2]['high']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Down high_low_diff: {high_low_diff}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time = time.time()
                if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"
                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time = current_time


             ## لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Text = None       
             if (FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low']) : #or (FrameRatesM5.iloc[-2]['high'] < FrameRatesM5.iloc[-3]['high']) :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       if  Now_c_L > Old_c_L :#and Now_c_H > Old_c_H :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[current_index : -2]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if high_low_diff < (200 * ATR_Value * 0.9) : return
                if round((round(abs((FrameRatesM5.iloc[current_index : -2]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff * 1000,1) > 50 : return

                PublicVarible.Baseroof = FrameRatesM5.iloc[current_index : -2]['high'].max()
                PublicVarible.Basefloor = FrameRatesM5.iloc[-2]['low']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Up high_low_diff: {high_low_diff}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time = time.time()
                if current_time - PublicVarible.last_execution_time >= 300:  
                   Text = f"{self.Pair}\n"
                   Text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"

                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time = current_time

             if FrameRatesM5.iloc[-2]['close'] > PublicVarible.Baseroof and PublicVarible.Baseroof != 0 : 
                print(f"price is {FrameRatesM5.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} ")
                if current_time - PublicVarible.last_execution_time >= 300:   
                   Text = f"price is {FrameRatesM5.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} "
                   #PromptToTelegram(Text)  
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

             if FrameRatesM5.iloc[-2]['close'] < PublicVarible.Basefloor and PublicVarible.Basefloor != 0 : 
                print(f"price is {FrameRatesM5.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor} ")
                if current_time - PublicVarible.last_execution_time >= 300:   
                   Text = f"price is {FrameRatesM5.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor}  "
                   #PromptToTelegram(Text)  
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


                
      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500