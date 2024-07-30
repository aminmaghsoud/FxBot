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
      TimeFrame = MT5.TIMEFRAME_M1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair == "XAUUSDb":
             return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV3 M15--------------")
          #Botdashboard(14 , self.Pair)
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             
             RatesM1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M1, 0, 120)
             if RatesM1 is not None:
                FrameRatesM1 = PD.DataFrame(RatesM1)
                if not FrameRatesM1.empty:
                   FrameRatesM1['datetime'] = PD.to_datetime(FrameRatesM1['time'], unit='s')
                   FrameRatesM1 = FrameRatesM1.drop('time', axis=1)
                   FrameRatesM1 = FrameRatesM1.set_index(PD.DatetimeIndex(FrameRatesM1['datetime']), drop=True)
                   
########################################################################################### بررسی شروط اولیه  #########################################################################################################
             current_datetime = datetime.now()
             LastCandle = FrameRatesM1.iloc[-1]
             minutes_to_exclude = [15,30, 45, 0]
             if (LastCandle['datetime'].hour in [0,1]) or (current_datetime.weekday() == 4 and current_datetime.hour >= 17) or LastCandle['datetime'].minute not in minutes_to_exclude : 
                Botdashboard(4 , self.Pair)
                return
             elif PublicVarible.CanOpenOrderST == False or PublicVarible.CanOpenOrder == False : 
                Botdashboard(36 , self.Pair)
                return
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 260)
             if RatesH1 is not None:
                   FrameRatesH1 = PD.DataFrame(RatesH1)
                   if not FrameRatesH1.empty:
                      FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                      FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                      FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)
                      SuperTH1 = supertrend(Pair = self.Pair , high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], length= 14 , multiplier= 3) #SuperTrend calculation
                      DirectionH1 = SuperTH1.iloc[-2][1]
                      PriceST3 = SuperTH1.iloc[-2][0]
             

             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 260)
             if RatesM15 is not None:
                   FrameRatesM15 = PD.DataFrame(RatesM15)
                   if not FrameRatesM15.empty:
                      FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                      FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                      FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)
                      SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 10 , multiplier = 4 ) #SuperTrend calculation
                      DirectionM15 = SuperTM15.iloc[-2][1]
                      PriceST2 = SuperTM15.iloc[-2][0]
                      
             if DirectionM15 != DirectionH1 : 
                return
             STH30 = PTA.stoch(high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], k= 14, d= 5, smooth_k= 5)   #Stochastic calculation 
                      
########################################################################################### بررسی شروط اولیه بیش فروش و بیش خرید  #########################################################################################################
             
             if DirectionH1 == 1 and  STH30.iloc[-1][0] > 99 : 
                Botdashboard(12 , self.Pair) 
                return     
             #elif DirectionH1 == 1 and MFIH1.iloc[-1] > 85 : 
             #   Botdashboard(42 , self.Pair)
             #   return
             elif DirectionH1 == -1 and STH30.iloc[-1][0] < 1 :
                Botdashboard(11 , self.Pair) 
                return     
             #elif DirectionH1 == -1 and MFIH1.iloc[-1] < 15 : 
             #   Botdashboard(43 , self.Pair)
             #   return

########################################################################################### بدنه استراتژی  #########################################################################################################
             init ()
             BuyAllow = 1
             SellAllow = 1
            #if SuperTH1.iloc[-2][0] == SuperTH1.iloc[-5][0] :
            #   BuyAllow = 0
            #   SellAllow = 0
                
             ################################ شرط معامله فروش  #####################################

             if DirectionH1 == 1  : 
                buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
                if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return
                
                
                BaseHigh = self.FindSwingHigh(FrameRatesM15, SymbolInfo.point,0,0,0)  
                if SellAllow == 1 : Botdashboard(63 , self.Pair)
                else : Botdashboard(64 , self.Pair)
                SymbolInfo = MT5.symbol_info(self.Pair)
                
                if BaseHigh == -1 and SellAllow :                                                                  ######### شرط اصلی پیدا کردن نقطه ورود به معامله ##########   STH30slope < 0 and RSIslope < -0.5 and StochRSI_k2 > 80 
                   write_trade_info_to_file(self.Pair ,"Buy" , BaseHigh, 0, 0, 0 , 0 ,0 , DirectionH1 )
                   EntryPrice = SymbolInfo.bid                                                                                        ######### قیمت  ورود به معامله ##########
                   Volume = self.CalcLotSize(Point= SymbolInfo.point)                                                                 #########  محاسه حجم ورود به معامله ##########
                   TP1 = FrameRatesM15.iloc[-3]['close']
                   SL = EntryPrice - ((TP1 - EntryPrice)* 0.7)                                                                         #########  تعیین حدسود معامله ########## 
                   if time.time() - PublicVarible.last_message_time >= 5 :
                       PublicVarible.last_message_time = time.time()
                       Text = "🔺 V3 -M15- Find Spike\n"
                       Text += f"{SymbolInfo.name}\n"
                       Text += "Sell\n"
                       Text += f"Volume: {str(Volume)}\n"
                       Text += f"Price: {str(EntryPrice)}\n"
                       Text += f"S/L: {str(SL)}\n"
                       Text += f"T/P: {str(TP1)}"
                       PromptToTelegram(Text)
                       print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"id:{PublicVarible.Id}- V3 M15") #########  ارسال اطلاعات فروش به تابع  ########## 
                   
             ############################# شرط معامله خرید  #####################################
                      
             if DirectionH1 == -1:     
                sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
                BaseLow = self.FindSwingLow(FrameRatesM15, SymbolInfo.point,0,0,0)
                if BuyAllow == 1 : Botdashboard(63 , self.Pair)
                else : Botdashboard(64 , self.Pair)
                SymbolInfo = MT5.symbol_info(self.Pair)
                
                if (BaseLow == 1) and BuyAllow :                                                        # ######## شرط اصلی پیدا کردن نقطه ورود به معامله ########## (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and RSIslope > 0.5  and StochRSI_k2 < 20  
                   EntryPrice = SymbolInfo.ask                                                           ######### قیمت  ورود به معامله ##########
                   Volume = self.CalcLotSize(Point= SymbolInfo.point)                                    #########  محاسه حجم ورود به معامله ##########
                   TP1 = FrameRatesM15.iloc[-3]['close'] 
                   SL = ((EntryPrice - TP1)* 0.7) + EntryPrice 
                   if time.time() - PublicVarible.last_message_time >= 5 :
                       write_trade_info_to_file(self.Pair ,"Sell" , BaseLow, 0, 0, 0 , 0 , 0 , DirectionH1 )
                       PublicVarible.last_message_time = time.time()
                       Text = "🔻 V3 -M15- Find Spike\n"
                       Text += f"{SymbolInfo.name}\n"
                       Text += "Buy\n"
                       Text += f"Volume: {str(Volume)}\n"
                       Text += f"Price: {str(EntryPrice)}\n"
                       Text += f"S/L: {str(SL)}\n"
                       Text += f"T/P: {str(TP1)}"
                       PromptToTelegram(Text)
                       print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"id:{PublicVarible.Id}- V3 M15") #########  ارسال اطلاعات فروش به تابع  ##########    
                      
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
          
          if C3 >= O3 and C1 < O1 and ((O1 - C1) > 100 * SymbolInfo.point) and C2 < O2 and ((O2 - C2)> 75 * SymbolInfo.point) and L1 < L2 and H1 < H2  and (O1 - C1) > (O2 - C2): 
             
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

          if C3 <= O3 and  C1 > O1 and ((C1 - O1) > 100 * SymbolInfo.point) and C2 > O2 and ((C2 - O2)> 75 * SymbolInfo.point) and L1 > L2 and H1 > H2 and (C1 - O1) > (C2 - O2): 
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
          Volume = 0.01
          return Volume
########################################################################################################
def CloseAllPosi(Pair:str):
     #MT5.Close(symbol= Pair)
   #  Prompt(f"Market trend is changed and All orders successfully closed, Balance: {str(GetBalance())}$")
   #  PromptToTelegram(Text= f"Market trend is changed and All orders successfully closed" + "\n" + f"💰 Balance: {str(GetBalance())}$")
     return True
########################################################################################################
