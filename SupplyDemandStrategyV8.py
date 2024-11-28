import pandas as PD
from Utility import *
from Trade import *
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style

class SupplyDemandStrategyV8():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M15
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M15 Range and Spike --")
          
          high_low_diff1 = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 250)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty: 
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)

             current_datetime = datetime.now()
             LastCandle = FrameRatesM15.iloc[-1]
             minutes_to_exclude = [0,15, 30, 45]
             if (LastCandle['datetime'].hour in [0 , 1]) or ((current_datetime.weekday() == 4 and current_datetime.hour > 20)) or (current_datetime.minute not in minutes_to_exclude ) :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return 
             ATR = PTA.atr(high = FrameRatesM15['high'],low = FrameRatesM15['low'], close = FrameRatesM15['close'],length=14)
             ATR_Value = ATR.iloc[-1]
             print("ATR_Value" , ATR_Value)
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()
             ## لگ نزولی
             end_index1 = -16
             current_index1 = -3
             count1 = 1
             high_low_diff1 = 0.0
            
             Text = None
             current_time1 = time.time()

             if (FrameRatesM15.iloc[-2]['high'] > FrameRatesM15.iloc[-3]['high']) : #or (FrameRatesM15.iloc[-2]['low'] > FrameRatesM15.iloc[-3]['low']) : 
                   while current_index1 > end_index1 : 
                       Now_c_H = FrameRatesM15.iloc[current_index1]['high']
                       Old_c_H = FrameRatesM15.iloc[current_index1 - 1]['high'] 
                       Now_c_L = FrameRatesM15.iloc[current_index1]['low']
                       Old_c_L = FrameRatesM15.iloc[current_index1 - 1]['low']
                       
                       if Now_c_H < Old_c_H : #and Now_c_L < Old_c_L :
                          count1 += 1 
                          current_index1 -= 1
                       else : 
                           break
             if count1 > 1 : 
                high_low_diff1 = round((abs( FrameRatesM15['low'].iloc[current_index1 : -2 ].min() - FrameRatesM15.iloc[current_index1]['high'])) / (SymbolInfo.point),2)
                if high_low_diff1 < (300 * ATR_Value * 0.9) : return
                if round(round(abs(FrameRatesM15.iloc[-2]['high'] - FrameRatesM15['low'].iloc[current_index1 : -2 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff1 * 1000,1) > 50 : return

                PublicVarible.Basefloor = FrameRatesM15['low'].iloc[current_index1 : -2 ].min()
                PublicVarible.Baseroof = FrameRatesM15.iloc[-2]['high']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Down high_low_diff1: {high_low_diff1}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time1 = time.time()
                if current_time1 - PublicVarible.last_execution_time1 >= 60:  
                   Text = f"{self.Pair}\n"
                   Text += f"M1️⃣5️⃣ لگ نزولی و رنج# ... 🔴🟣 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff1, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count1}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff1 * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime1.hour}:{current_datetime1.minute}"
                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time1 = current_time1


             ## لگ صعودی
             end_index1 = -16
             current_index1 = -3
             count1 = 1
             high_low_diff1 = 0.0
             Text = None       
             if (FrameRatesM15.iloc[-2]['low'] < FrameRatesM15.iloc[-3]['low']) : #or (FrameRatesM15.iloc[-2]['high'] < FrameRatesM15.iloc[-3]['high']) :
                   while current_index1 > end_index1 : 
                       Now_c_H = FrameRatesM15.iloc[current_index1]['high']
                       Old_c_H = FrameRatesM15.iloc[current_index1 - 1]['high'] 
                       Now_c_L = FrameRatesM15.iloc[current_index1]['low']
                       Old_c_L = FrameRatesM15.iloc[current_index1 - 1]['low']
                       if  Now_c_L > Old_c_L :#and Now_c_H > Old_c_H :
                          count1 += 1 
                          current_index1 -= 1
                       else : 
                           break
             if count1 > 1 : 
                high_low_diff1 = round((abs(FrameRatesM15.iloc[current_index1 : -2]['high'].max() - FrameRatesM15.iloc[current_index1]['low'])) / (SymbolInfo.point) , 2)
                if high_low_diff1 < (300 * ATR_Value * 0.9) : return
                if round((round(abs((FrameRatesM15.iloc[current_index1 : -2]['high'].max()) - ( FrameRatesM15.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff1 * 1000,1) > 50 : return

                PublicVarible.Baseroof = FrameRatesM15.iloc[current_index1 : -2]['high'].max()
                PublicVarible.Basefloor = FrameRatesM15.iloc[-2]['low']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Up high_low_diff1: {high_low_diff1}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time1 = time.time()
                if current_time1 - PublicVarible.last_execution_time1 >= 60:  
                   Text = f"{self.Pair}\n"
                   Text += f"M1️⃣5️⃣ لگ صعودی و رنج# ... 🟢🟣 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff1, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count1}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff1 * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime1.hour}:{current_datetime1.minute}"

                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time1 = current_time1

             """if FrameRatesM15.iloc[-2]['close'] > PublicVarible.Baseroof and PublicVarible.Baseroof != 0 : 
                print(f"price is {FrameRatesM15.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} ")
                if current_time1 - PublicVarible.last_execution_time1 >= 300:   
                   Text = f"price is {FrameRatesM15.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} "
                   #PromptToTelegram(Text)  
                   PublicVarible.last_execution_time1 = current_time1  
#Buy
                buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
                if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return

             if FrameRatesM15.iloc[-2]['close'] < PublicVarible.Basefloor and PublicVarible.Basefloor != 0 : 
                print(f"price is {FrameRatesM15.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor} ")
                if current_time1 - PublicVarible.last_execution_time1 >= 300:   
                   Text = f"price is {FrameRatesM15.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor}  "
                   #PromptToTelegram(Text)  
                   PublicVarible.last_execution_time1 = current_time1  
#Sell
                sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return


                """
      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500