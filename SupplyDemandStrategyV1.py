#from math import floor
#from mimetypes import init
#from multiprocessing.pool import CLOSE
#from pickle import NONE
#from xmlrpc.client import DateTime
#from matplotlib.colors import Normalize
import pandas_ta as PTA
import pandas as PD
#from scipy.signal import normalize
from Utility import *
from Trade import *
import PublicVarible
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import ta
#import numpy as np
from datetime import datetime
import PublicVarible


class SupplyDemandStrategyV1():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M15
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV1 Swing ...  --------------")
          if self.Pair != 'XAUUSDb' : 
              return
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)

             """RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 250)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty:
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)
                   
             RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 250)
             if RatesH1 is not None:
                FrameRatesH1 = PD.DataFrame(RatesH1)
                if not FrameRatesH1.empty:
                   FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                   FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                   FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)"""

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             
             O2 = FrameRatesM5.iloc[-2]['open']
             C2 = FrameRatesM5.iloc[-2]['close']
             H2 = FrameRatesM5.iloc[-2]['high']
             L2 = FrameRatesM5.iloc[-2]['low']
             H3 = FrameRatesM5.iloc[-3]['high']
             L3 = FrameRatesM5.iloc[-3]['low'] 
             
             if abs(C2 - O2) / SymbolInfo.point < 15 :
                print("Candle is small ...")
                return

             Sell_pin = 0
             Buy_pin = 0

             #if C2 < O2 and (abs(L2-C2)/SymbolInfo.point) < ((abs(C2-O2)/SymbolInfo.point)*0.5) and C2 < L3 : 
             if FrameRatesM5.iloc[-2]['close'] > PublicVarible.Baseroof  or FrameRatesM5.iloc[-2]['close'] < PublicVarible.Basefloor  and PublicVarible.Baseroof != 0 :
               for i in range(-2 , -3 , -1) : 
                   if FrameRatesM5.iloc[i]['close'] > FrameRatesM5.iloc[i]['open'] :
                        Up_shadow = abs(FrameRatesM5.iloc[i]['high'] - FrameRatesM5.iloc[i]['close']) / SymbolInfo.point
                   else : 
                        Up_shadow = abs(FrameRatesM5.iloc[i]['high'] - FrameRatesM5.iloc[i]['open'] ) / SymbolInfo.point
                   
                   if FrameRatesM5.iloc[i]['close'] > FrameRatesM5.iloc[i]['open'] :
                        Down_shadow = abs(FrameRatesM5.iloc[i]['low'] - FrameRatesM5.iloc[i]['open']) / SymbolInfo.point
                   else : 
                        Down_shadow = abs(FrameRatesM5.iloc[i]['low'] - FrameRatesM5.iloc[i]['close'] ) / SymbolInfo.point

                   body = abs(FrameRatesM5.iloc[i]['close'] - FrameRatesM5.iloc[i]['open']) / SymbolInfo.point

                   if (Up_shadow * 0.5) > body and (Up_shadow * 0.35) > Down_shadow  : 
                       Sell_pin = 1
                       print("Signal Bar Founded ...")
                       break
                   
             #elif C2 > O2 and (abs(H2-C2)/SymbolInfo.point) < ((abs(C2-O2)/SymbolInfo.point)*0.5) and C2 > H3 : 
             elif FrameRatesM5.iloc[-2]['close'] > PublicVarible.Baseroof  or FrameRatesM5.iloc[-2]['close'] < PublicVarible.Basefloor  and PublicVarible.Baseroof != 0 :
               for i in range(-2 , -3 , -1) : 
                   if FrameRatesM5.iloc[i]['close'] > FrameRatesM5.iloc[i]['open'] :
                        Down_shadow = abs(FrameRatesM5.iloc[i]['low'] - FrameRatesM5.iloc[i]['open']) / SymbolInfo.point
                   else : 
                        Down_shadow = abs(FrameRatesM5.iloc[i]['low'] - FrameRatesM5.iloc[i]['close'] ) / SymbolInfo.point

                   if FrameRatesM5.iloc[i]['close'] > FrameRatesM5.iloc[i]['open'] :
                        Up_shadow = abs(FrameRatesM5.iloc[i]['high'] - FrameRatesM5.iloc[i]['close']) / SymbolInfo.point
                   else : 
                        Up_shadow = abs(FrameRatesM5.iloc[i]['high'] - FrameRatesM5.iloc[i]['open'] ) / SymbolInfo.point
                   

                   body = abs(FrameRatesM5.iloc[i]['close'] - FrameRatesM5.iloc[i]['open']) / SymbolInfo.point
                   if (Down_shadow * 0.5) > body and (Down_shadow * 0.5) > Up_shadow : 
                       Buy_pin = 1
                       print("Signal Bar Founded ...")
                       break
             
             elif FrameRatesM5.iloc[-2]['close'] > FrameRatesM5.iloc[-2]['open'] and FrameRatesM5.iloc[-2]['close'] == FrameRatesM5.iloc[-2]['high'] and FrameRatesM5.iloc[-2]['open'] == FrameRatesM5.iloc[-2]['low'] :
                  if  (abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / SymbolInfo.point) > 20 :
                      Buy_pin = 2
                 
             elif FrameRatesM5.iloc[-2]['close'] < FrameRatesM5.iloc[-2]['open'] and FrameRatesM5.iloc[-2]['close'] == FrameRatesM5.iloc[-2]['low'] and FrameRatesM5.iloc[-2]['open'] == FrameRatesM5.iloc[-2]['high'] :
                  if  (abs(FrameRatesM5.iloc[-2]['close'] - FrameRatesM5.iloc[-2]['open']) / SymbolInfo.point) > 20 :
                      Sell_pin = 2
             
             else : 
                   print("Swing Not Found and Return")
                   return
             

             """SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionM15 = SuperTM15.iloc[-2][1]
             Direction15 = "UP" if DirectionM15 == 1 else "DOWN"
             PriceST1 = SuperTM15.iloc[-2][0]

             SuperTH1 = supertrend(Pair = self.Pair , high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionH1 = SuperTH1.iloc[-2][1]
             Direction1 = "UP" if DirectionH1 == 1 else "DOWN"
             PriceST1 = SuperTH1.iloc[-2][0]

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
             
             if Direction_ichi == 1 and DirectionH1 == 1 and DirectionM15 == 1 :
                Market_Direction = 1
             elif Direction_ichi == -1 and DirectionH1 == -1 and DirectionM15 == -1 :
                Market_Direction = -1
             else : Market_Direction = 0"""

             if Sell_pin == 1 :
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['low'] - FrameRatesM5.iloc[-3]['high'])) / (SymbolInfo.point),2)
                if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] : Basefloor = FrameRatesM5.iloc[-2]['low'] 
                else : Basefloor = FrameRatesM5.iloc[-3]['low']
                Baseroof = FrameRatesM5.iloc[-2]['high']
                if True :
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"سوئینگ سقف ... 🔴🔴 \n"
                      
                      #if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      #elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      #else : Text += f"روند مارکت : No Direc..."  

                      PromptToTelegram(Text)
            
             if Buy_pin == 1 :
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[-3]['low'])) / (SymbolInfo.point) , 2)
                if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high'] : Baseroof = FrameRatesM5.iloc[-2]['high']  
                else : Baseroof = FrameRatesM5.iloc[-3]['high'] 
                Basefloor = FrameRatesM5.iloc[-2]['low']
                if  True : 
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"سوئینگ کف... 🟢🟢 \n"
                      #if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      #elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      #else : Text += f"روند مارکت : No Direc..."  
                      PromptToTelegram(Text)

             if Sell_pin == 2 :
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['low'] - FrameRatesM5.iloc[-3]['high'])) / (SymbolInfo.point),2)
                if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] : Basefloor = FrameRatesM5.iloc[-2]['low'] 
                else : Basefloor = FrameRatesM5.iloc[-3]['low']
                Baseroof = FrameRatesM5.iloc[-2]['high']
                if True :
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"ماربوزو قرمز... 🔴🔴 \n"
                      PromptToTelegram(Text)
            
             if Buy_pin == 2 :
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[-3]['low'])) / (SymbolInfo.point) , 2)
                if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high'] : Baseroof = FrameRatesM5.iloc[-2]['high']  
                else : Baseroof = FrameRatesM5.iloc[-3]['high'] 
                Basefloor = FrameRatesM5.iloc[-2]['low']
                if  True : 
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      Text += f"ماربوزو سبز... 🟢🟢 \n"
                      PromptToTelegram(Text)       
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500