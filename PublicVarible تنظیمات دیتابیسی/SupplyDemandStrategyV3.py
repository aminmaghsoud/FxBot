import pandas as PD
from Utility import *
from Trade import *
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV3():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_H1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 H1 Range and Spike --")
          
          high_low_diff1 = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 250)
             if RatesH1 is not None:
                FrameRatesH1 = PD.DataFrame(RatesH1)
                if not FrameRatesH1.empty: 
                   FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                   FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                   FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)

             current_datetime = datetime.now()
             LastCandle = FrameRatesH1.iloc[-1]
             minutes_to_exclude = [0, 1]
             if (LastCandle['datetime'].hour in [0 , 1]) or ((current_datetime.weekday() == 4 and current_datetime.hour > 20)) or (current_datetime.minute not in minutes_to_exclude ) :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return 
             ATR = PTA.atr(high = FrameRatesH1['high'],low = FrameRatesH1['low'], close = FrameRatesH1['close'],length=14)
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

             if (FrameRatesH1.iloc[-2]['high'] > FrameRatesH1.iloc[-3]['high']) : #or (FrameRatesH1.iloc[-2]['low'] > FrameRatesH1.iloc[-3]['low']) : 
                   while current_index1 > end_index1 : 
                       Now_c_H = FrameRatesH1.iloc[current_index1]['high']
                       Old_c_H = FrameRatesH1.iloc[current_index1 - 1]['high'] 
                       Now_c_L = FrameRatesH1.iloc[current_index1]['low']
                       Old_c_L = FrameRatesH1.iloc[current_index1 - 1]['low']
                       
                       if Now_c_H < Old_c_H : #and Now_c_L < Old_c_L :
                          count1 += 1 
                          current_index1 -= 1
                       else : 
                           break
             if count1 > 1 : 
                high_low_diff1 = round((abs( FrameRatesH1['low'].iloc[current_index1 : -2 ].min() - FrameRatesH1.iloc[current_index1]['high'])) / (SymbolInfo.point),2)
                if high_low_diff1 < (300 * ATR_Value * 0.9) : return
                if round(round(abs(FrameRatesH1.iloc[-2]['high'] - FrameRatesH1['low'].iloc[current_index1 : -2 ].min()) / (SymbolInfo.point) / 10, 2) / high_low_diff1 * 1000,1) > 50 : return

                PublicVarible.Basefloor = FrameRatesH1['low'].iloc[current_index1 : -2 ].min()
                PublicVarible.Baseroof = FrameRatesH1.iloc[-2]['high']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Down high_low_diff1: {high_low_diff1}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time1 = time.time()
                if current_time1 - PublicVarible.last_execution_time1 >= 60:  
                   Text = f"{self.Pair}\n"
                   Text += f"H1️⃣ لگ نزولی و رنج# ... 🔴🟡 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff1, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count1}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff1 * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"
                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time1 = current_time1


             ## لگ صعودی
             end_index1 = -16
             current_index1 = -3
             count1 = 1
             high_low_diff1 = 0.0
             Text = None       
             if (FrameRatesH1.iloc[-2]['low'] < FrameRatesH1.iloc[-3]['low']) : #or (FrameRatesH1.iloc[-2]['high'] < FrameRatesH1.iloc[-3]['high']) :
                   while current_index1 > end_index1 : 
                       Now_c_H = FrameRatesH1.iloc[current_index1]['high']
                       Old_c_H = FrameRatesH1.iloc[current_index1 - 1]['high'] 
                       Now_c_L = FrameRatesH1.iloc[current_index1]['low']
                       Old_c_L = FrameRatesH1.iloc[current_index1 - 1]['low']
                       if  Now_c_L > Old_c_L :#and Now_c_H > Old_c_H :
                          count1 += 1 
                          current_index1 -= 1
                       else : 
                           break
             if count1 > 1 : 
                high_low_diff1 = round((abs(FrameRatesH1.iloc[current_index1 : -2]['high'].max() - FrameRatesH1.iloc[current_index1]['low'])) / (SymbolInfo.point) , 2)
                if high_low_diff1 < (300 * ATR_Value * 0.9) : return
                if round((round(abs((FrameRatesH1.iloc[current_index1 : -2]['high'].max()) - ( FrameRatesH1.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / high_low_diff1 * 1000,1) > 50 : return

                PublicVarible.Baseroof = FrameRatesH1.iloc[current_index1 : -2]['high'].max()
                PublicVarible.Basefloor = FrameRatesH1.iloc[-2]['low']
                range_height = round(abs(PublicVarible.Baseroof - PublicVarible.Basefloor) / (SymbolInfo.point) / 10, 2)
                print(f"Up high_low_diff1: {high_low_diff1}  and  PublicVarible.Baseroof: {PublicVarible.Baseroof}  and  PublicVarible.Basefloor: {PublicVarible.Basefloor} and  Range arraye : {abs(PublicVarible.Basefloor - PublicVarible.Baseroof) / (SymbolInfo.point)} \n")
                current_time1 = time.time()
                if current_time1 - PublicVarible.last_execution_time1 >= 60:  
                   Text = f"{self.Pair}\n"
                   Text += f"H1️⃣ لگ صعودی و رنج# ... 🟢🟡 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff1, 2) / 10} pip\n"
                   Text += f"تعداد کندل: {count1}\n"
                   Text += f"سقف: {PublicVarible.Baseroof} \n"
                   Text += f"کف : {PublicVarible.Basefloor} \n"
                   Text += f"نسبت رنج به لگ: {round(range_height / high_low_diff1 * 1000,1) } % \n"
                   Text += f"ارتفاع رنج: {range_height} pip \n"
                   Text += f"حجم مجاز : {round(Balace * 0.0015 / range_height , 2)} \n"
                   Text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute}"

                   PromptToTelegram(Text)
                   PublicVarible.last_execution_time1 = current_time1

             """if FrameRatesH1.iloc[-2]['close'] > PublicVarible.Baseroof and PublicVarible.Baseroof != 0 : 
                print(f"price is {FrameRatesH1.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} ")
                if current_time1 - PublicVarible.last_execution_time1 >= 300:   
                   Text = f"price is {FrameRatesH1.iloc[-2]['close']} and Upper Roof {PublicVarible.Baseroof} "
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

             if FrameRatesH1.iloc[-2]['close'] < PublicVarible.Basefloor and PublicVarible.Basefloor != 0 : 
                print(f"price is {FrameRatesH1.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor} ")
                if current_time1 - PublicVarible.last_execution_time1 >= 300:   
                   Text = f"price is {FrameRatesH1.iloc[-2]['close']} and Under floor {PublicVarible.Basefloor}  "
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