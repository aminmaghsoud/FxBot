
import pandas as PD
from Utility import *
from Trade import *
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style

class SupplyDemandStrategyV3():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_H1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV3 H1 Spike --------------")
          if self.Pair != 'XAUUSDb' : 
              return
          high_low_diff = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 250)
             if RatesH1 is not None:
                FrameRatesH1 = PD.DataFrame(RatesH1)
                if not FrameRatesH1.empty:
                   FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                   FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                   FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)
             
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
            
             ## لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None
             if (FrameRatesH1.iloc[-2]['high'] > FrameRatesH1.iloc[-3]['high']) : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesH1.iloc[current_index]['high']
                       Old_c_H = FrameRatesH1.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesH1.iloc[current_index]['low']
                       Old_c_L = FrameRatesH1.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
                
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesH1.iloc[-2]['low'] - FrameRatesH1.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if FrameRatesH1.iloc[-2]['low'] < FrameRatesH1.iloc[-3]['low'] : Basefloor = FrameRatesH1.iloc[-2]['low'] 
                else : Basefloor = FrameRatesH1.iloc[-3]['low']
                Baseroof = FrameRatesH1.iloc[-2]['high']
                print(f"Down high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof) / (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.75 ):
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 3600 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f" H1 لگ نزولی# ... 🔴 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"تعداد کندل: {count}\n"
                      PromptToTelegram(Text)
                      
             ## لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None       
             if FrameRatesH1.iloc[-2]['low'] < FrameRatesH1.iloc[-3]['low'] :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesH1.iloc[current_index]['high']
                       Old_c_H = FrameRatesH1.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesH1.iloc[current_index]['low']
                       Old_c_L = FrameRatesH1.iloc[current_index - 1]['low']
                       if  Now_c_L > Old_c_L :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesH1.iloc[-2]['high'] - FrameRatesH1.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if FrameRatesH1.iloc[-2]['high'] > FrameRatesH1.iloc[-3]['high'] : Baseroof = FrameRatesH1.iloc[-2]['high']  
                else : Baseroof = FrameRatesH1.iloc[-3]['high'] 
                Basefloor = FrameRatesH1.iloc[-2]['low']
                print(f"Up high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof)/ (SymbolInfo.point)} \n")
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.75 ) : 
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 3600 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"H1لگ صعودی ... 🟢 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"تعداد کندل: {count}\n"
                      PromptToTelegram(Text)
                     
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500