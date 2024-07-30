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

class SupplyDemandStrategyV4():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair != "XAUUSDb":
             return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV4 M5 Spike --------------")
          #Botdashboard(14 , self.Pair)
          high_low_diff = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 30)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
########################################################################################### بررسی شروط اولیه  #########################################################################################################
             """current_datetime = datetime.now()
             LastCandle = FrameRatesM5.iloc[-1]
             minutes_to_exclude = [4, 5, 9, 10, 14, 15, 19, 20, 24, 25, 29, 30, 34, 35, 39, 40, 44, 45, 49, 50, 54, 55, 59, 0]
             if (LastCandle['datetime'].hour in [0,1]) or (current_datetime.weekday() == 4 and current_datetime.hour >= 17) or LastCandle['datetime'].minute not in minutes_to_exclude : 
                Botdashboard(4 , self.Pair)
                return
             elif PublicVarible.CanOpenOrderST == False or PublicVarible.CanOpenOrder == False : 
                Botdashboard(36 , self.Pair)
                return"""
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 260)
             if RatesM30 is not None:
                   FrameRatesM30 = PD.DataFrame(RatesM30)
                   if not FrameRatesM30.empty:
                      FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
                      FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
                      FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)
             SuperT30 = supertrend(Pair = self.Pair , high= FrameRatesM30['high'], low= FrameRatesM30['low'], close= FrameRatesM30['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionM30 = SuperT30.iloc[-2][1]
             PriceST3 = SuperT30.iloc[-2][0]
             
             
             if DirectionM30 == -1  :    
                if  FrameRatesM5.iloc[-1]['high'] > FrameRatesM5.iloc[-2]['high'] : 
                    end_index = (len(FrameRatesM5) - 1) * -1
                    current_index = -2
                    count = 0
                    high_low_diff = 0
                    Basefloor = None
                    Baseroof = None
                    while current_index > end_index :
                        print (f"FrameRatesM5.iloc[{current_index}]['high']: " ,FrameRatesM5.iloc[current_index]['high'])
                        if FrameRatesM5.iloc[current_index]['high'] > FrameRatesM5.iloc[current_index - 1]['high'] and FrameRatesM5.iloc[current_index]['low'] > FrameRatesM5.iloc[current_index - 1]['low']:
                            count += 1
                            high_low_diff = FrameRatesM5.iloc[count * -1 ]['high'] - FrameRatesM5.iloc[-2]['low']
                            print("high_low_diff: ",high_low_diff)
                            if high_low_diff > 3 : #and (FrameRatesM5.iloc[-1]['high'] - FrameRatesM5.iloc[-2]['low']) < high_low_diff * 0.25 : 
                               if time.time() - PublicVarible.last_message_time >= 58 :
                                  PublicVarible.last_message_time = time.time()
                                  PromptToTelegram(f"لگ نزولی {self.Pair} در روند نزولی 5 دقیقه بررسی شود. تعداد {count} ")
                            current_index -= 1
                        else:
                            Basefloor = FrameRatesM5.iloc[-3]['low']
                            Baseroof = FrameRatesM5.iloc[-2]['high'] 
                            print("Basefloor: ",Basefloor)
                            print("Baseroof: ",Baseroof)
                            break
                        
                if high_low_diff > 3 and Basefloor is not None and Baseroof is not None:
                   if FrameRatesM5.iloc[-1]['close'] > Baseroof and FrameRatesM5.iloc[-2]['close'] > Baseroof:
                       PromptToTelegram("سیگنال خرید طلا در روند صعودی 5 دقیقه بررسی شود")
                   elif FrameRatesM5.iloc[-1]['close'] < Basefloor and FrameRatesM5.iloc[-2]['close'] < Basefloor:
                       PromptToTelegram("سیگنال فروش طلا در روند صعودی 5 دقیقه بررسی شود")
                       

                  #EntryPrice = SymbolInfo.bid                                                                                        ######### قیمت  ورود به معامله ##########
                  #Volume = self.CalcLotSize(Point= SymbolInfo.point)                                                                 #########  محاسه حجم ورود به معامله ##########
                  #SL = PriceST2 #FrameRatesM1.iloc[-2]['high'] + (20 * SymbolInfo.point)                                                        #########  تعیین حدضرر معامله #########
                  #TP1 = EntryPrice - (100 * SymbolInfo.point)                                                                         #########  تعیین حدسود معامله ########## 
                  #if time.time() - PublicVarible.last_message_time >= 280 :
                  #    PublicVarible.last_message_time = time.time()
                  #    Text = "🔻 Find Spike\n"
                  #    Text += f"{SymbolInfo.name}\n"
                  #    Text += "Sell\n"
                  #    Text += f"Volume: {str(Volume)}\n"
                  #    Text += f"Price: {str(EntryPrice)}\n"
                  #    Text += f"S/L: {str(SL)}\n"
                  #    Text += f"T/P: {str(TP1)}"
                  #    PromptToTelegram(Text)
                  #    print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  #    Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                  #    OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"id:{PublicVarible.Id}- V1 M5") #########  ارسال اطلاعات فروش به تابع  ########## 
                   
             ############################# شرط معامله خرید  #####################################
             
         
             if DirectionM30 == 1  :    
                if  FrameRatesM5.iloc[-1]['low'] < FrameRatesM5.iloc[-2]['low'] : 
                    end_index = (len(FrameRatesM5) - 1) * -1
                    current_index = -2
                    count = 0
                    high_low_diff = 0
                    Basefloor = None
                    Baseroof = None
                    while current_index > end_index :
                        print (f"FrameRatesM5.iloc[{current_index}]['high']: " ,FrameRatesM5.iloc[current_index]['high'])
                        if FrameRatesM5.iloc[current_index]['high'] < FrameRatesM5.iloc[current_index - 1]['high'] and FrameRatesM5.iloc[current_index]['low'] < FrameRatesM5.iloc[current_index - 1]['low']:
                            count += 1
                            high_low_diff = FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[count * -1 ]['low'] 
                            print("high_low_diff: ",high_low_diff)
                            if high_low_diff > 3 : # and (FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[-1]['low']) < high_low_diff * 0.25 :    
                               if time.time() - PublicVarible.last_message_time >= 58 :
                                  PublicVarible.last_message_time = time.time()
                                  PromptToTelegram("لگ صعودی طلا در روند صعودی 5 دقیقه بررسی شود ")
                                  
                            current_index -= 1
                        else:
                            Basefloor = FrameRatesM5.iloc[-1]['low']
                            Baseroof = FrameRatesM5.iloc[-2]['high'] 
                            print("Basefloor: ",Basefloor)
                            print("Baseroof: ",Baseroof)
                            break
                if high_low_diff > 3 and Basefloor is not None and Baseroof is not None:
                   if FrameRatesM5.iloc[-1]['close'] > Baseroof and FrameRatesM5.iloc[-2]['close'] > Baseroof:
                       PromptToTelegram("سیگنال خرید طلا در روند صعودی 5 دقیقه بررسی شود")
                   elif FrameRatesM5.iloc[-1]['close'] < Basefloor and FrameRatesM5.iloc[-2]['close'] < Basefloor:
                       PromptToTelegram("سیگنال فروش طلا در روند صعودی 5 دقیقه بررسی شود")
   

                #EntryPrice = SymbolInfo.ask                                                           ######### قیمت  ورود به معامله ##########
                #Volume = self.CalcLotSize(Point= SymbolInfo.point)                                    #########  محاسه حجم ورود به معامله ##########
                #SL = PriceST2 #FrameRatesM1.iloc[-2]['low'] + (20 * SymbolInfo.point)  
                #TP1 = EntryPrice + (100 * SymbolInfo.point)   
                #if time.time() - PublicVarible.last_message_time >= 280 :
                #    write_trade_info_to_file(self.Pair ,"Buy" , BaseLow, 0, 0, 0 , 0 , 0 , DirectionM30 )
                #    PublicVarible.last_message_time = time.time()
                #    Text = "🔺 Find Spike\n"
                #    Text += f"{SymbolInfo.name}\n"
                #    Text += "Buy\n"
                #    Text += f"Volume: {str(Volume)}\n"
                #    Text += f"Price: {str(EntryPrice)}\n"
                #    Text += f"S/L: {str(SL)}\n"
                #    Text += f"T/P: {str(TP1)}"
                #    PromptToTelegram(Text)
                #    print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                #    Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                #    OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"id:{PublicVarible.Id}- V1 M5") #########  ارسال اطلاعات فروش به تابع  ##########    
                #   
########################################################################################################
      def FindSwingHigh(self, FrameRates, Point,M5RSI,StochRSI_k2,RSIslope):
          SymbolInfo = MT5.symbol_info(self.Pair)
          Base = 0
          O1 = FrameRates.iloc[-2]['open']
          C1 = FrameRates.iloc[-2]['close']
          L1 = FrameRates.iloc[-2]['low']
          H1 = FrameRates.iloc[-2]['high']
          O2 = FrameRates.iloc[-3]['open']
          H2 = FrameRates.iloc[-3]['high']
          L2 = FrameRates.iloc[-3]['low']
          C2 = FrameRates.iloc[-3]['close']
          O3 = FrameRates.iloc[-4]['open']
          C3 = FrameRates.iloc[-4]['close']
          
          if C3 >= O3 and C1 < O1 and ((O1 - C1) > 120 * SymbolInfo.point) and C2 < O2 and ((O2 - C2)> 90 * SymbolInfo.point) and L1 < L2 and H1 < H2  and (O1 - C1) > (O2 - C2): 
             
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #    PublicVarible.last_message_time = time.time()
             #    PromptToTelegram(f"الگوی سر و شانه نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Leg found ...")
             Base = -1 

          return (Base)

########################################################################################################
      def FindSwingLow(self, FrameRates, Point,M5RSI,StochRSI_k2,RSIslope):
          SymbolInfo = MT5.symbol_info(self.Pair)
          Base = 0
          O1 = FrameRates.iloc[-2]['open']
          C1 = FrameRates.iloc[-2]['close']
          L1 = FrameRates.iloc[-2]['low']
          H1 = FrameRates.iloc[-2]['high']
          O2 = FrameRates.iloc[-3]['open']
          H2 = FrameRates.iloc[-3]['high']
          L2 = FrameRates.iloc[-3]['low']
          C2 = FrameRates.iloc[-3]['close']
          O3 = FrameRates.iloc[-4]['open']
          C3 = FrameRates.iloc[-4]['close']

          if C3 <= O3 and  C1 > O1 and ((C1 - O1) > 120 * SymbolInfo.point) and C2 > O2 and ((C2 - O2)> 90 * SymbolInfo.point) and L1 > L2 and H1 > H2 and (C1 - O1) > (C2 - O2): 
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #   PublicVarible.last_message_time = time.time()
             #   #PromptToTelegram(f"الگوی سر و شانه صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Leg found ...")
             Base = 1 
              
          return (Base)

########################################################################################################
      def CalcLotSize(self,Point):
        
         #if self.Pair == 'XAUUSDb' : 
         #   Volume = GetBalance() // 150 * 0.01
         #else :  Volume = GetBalance() // 70 * 0.01
         # print(" Volume: ",Volume)
         #if  Volume < 0.01 : 
          Volume = 0.02
          return Volume
########################################################################################################
def CloseAllPosi(Pair:str):
     #MT5.Close(symbol= Pair)
   #  Prompt(f"Market trend is changed and All orders successfully closed, Balance: {str(GetBalance())}$")
   #  PromptToTelegram(Text= f"Market trend is changed and All orders successfully closed" + "\n" + f"💰 Balance: {str(GetBalance())}$")
     return True
########################################################################################################
