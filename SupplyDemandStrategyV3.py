from math import floor
from mimetypes import init
from multiprocessing.pool import CLOSE
from pickle import NONE
from xmlrpc.client import DateTime
from matplotlib.colors import Normalize
import pandas_ta as PTA
import pandas as PD
from scipy.signal import normalize
from Utility import *
from Trade import *
import PublicVarible
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import ta
import numpy as np
from datetime import datetime


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
             
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 250)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty:
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)

             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)   
             
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             AA , BB = PTA.ichimoku( high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'] , tenkan= 9 , kijun= 26 , senkou= 52 )
             senkou_a = BB['ISA_9'].iloc[-1]
             senkou_b = BB['ISB_26'].iloc[-1]
             if senkou_a > senkou_b : 
                Direction_ichi = 1
                Color_ichi = "Green"
             elif senkou_b > senkou_a : 
                Direction_ichi = -1 
                Color_ichi = "Red"
             else : 
                Direction_ichi = 0 
                Color_ichi = "Yellow"

             SuperTH1 = supertrend(Pair = self.Pair , high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionH1 = SuperTH1.iloc[-2][1]
             Direction = "UP" if DirectionH1 == 1 else "DOWN"
             PriceST3 = SuperTH1.iloc[-2][0]
             
             SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 14 , multiplier= 4) #SuperTrend calculation
             DirectionM15 = SuperTM15.iloc[-2][1]
             Direction15 = "Green" if DirectionM15 == 1 else "Red"
             PriceST1 = SuperTM15.iloc[-2][0]
             print("SupertT Color : ",Direction15)

             if Direction_ichi == 1 and DirectionH1 == 1 and DirectionM15 == 1 :
                Market_Direction = 1
             elif Direction_ichi == -1 and DirectionH1 == -1 and DirectionM15 == -1 :
                Market_Direction = -1
             else : Market_Direction = 0


             ## لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None
             if (FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high']) : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
                
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['low'] - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 150) or (self.Pair != 'XAUUSDb'and high_low_diff < 100)) :
                   return
                                
                if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] : Basefloor = FrameRatesM5.iloc[-2]['low'] 
                else : Basefloor = FrameRatesM5.iloc[-3]['low']
                Baseroof = FrameRatesM5.iloc[-2]['high']
                print(f"Down high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof) / (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.75 ):
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"لگ نزولی# ... 🔴 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"تعداد کندل: {count}\n"
                      if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      else : Text += f"روند مارکت : No Direc..."  
                      PromptToTelegram(Text)
                      
             ## لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None       
             if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       if  Now_c_L > Old_c_L :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 150) or (self.Pair != 'XAUUSDb'and high_low_diff < 100)) :
                   return
                if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high'] : Baseroof = FrameRatesM5.iloc[-2]['high']  
                else : Baseroof = FrameRatesM5.iloc[-3]['high'] 
                Basefloor = FrameRatesM5.iloc[-2]['low']
                print(f"Up high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof)/ (SymbolInfo.point)} \n")
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.75 ) : 
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"لگ صعودی ... 🟢 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"تعداد کندل: {count}\n"
                      if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      else : Text += f"روند مارکت : No Direc..."  
                      PromptToTelegram(Text)
                     
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500