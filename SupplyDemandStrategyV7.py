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

class SupplyDemandStrategyV7():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          BaseHigh = BaseLow = None 
          RSI = ST1 = DirectionST1 = PriceST1 = RatesM5 = RatesM1 = FrameRatesM1 = None 
          FrameRatesM5 = RatesH1 =  FrameRatesH1 = SuperTH1 = DirectionH1 = PriceST2 = MFIH1 = None 
          STH30 = StochRSI =  StochRSI_k2 = RSIslope = RatesH30 = FrameRatesH30 = None 
          M5RSI = 0.0
          Botdashboard(1 , self.Pair)
          SymbolInfo = MT5.symbol_info(self.Pair)
          
          if SymbolInfo is not None :
             RatesM1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M1, 0, 120)
             if RatesM1 is not None:
                FrameRatesM1 = PD.DataFrame(RatesM1)
                if not FrameRatesM1.empty:
                   FrameRatesM1['datetime'] = PD.to_datetime(FrameRatesM1['time'], unit='s')
                   FrameRatesM1 = FrameRatesM1.drop('time', axis=1)
                   FrameRatesM1 = FrameRatesM1.set_index(PD.DatetimeIndex(FrameRatesM1['datetime']), drop=True)
                   
 ############################################################## position Modify ###############################################################################

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
                                 if SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.7 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

                                 #if M5RSI > 90 :
                                 #   MT5.Close(symbol= self.Pair)
                                 #   PromptToTelegram(Text= f"{self.Pair} ❎ Buy Posision successfully closed by RSI Contoroler (>90)" + "\n" + f"💰 Balance: {str(GetBalance())}$")
             #else:
                #print(" No Buy positions found.")
             
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
                                 if SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.7 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")
                                 
                                 #if M5RSI < 10 :
                                 #   MT5.Close(symbol= self.Pair)
                                 #   PromptToTelegram(Text= f"{self.Pair} ❎ Sell Posision successfully closed by RSI Contoroler (<10)" + "\n" + f"💰 Balance: {str(GetBalance())}$")
             #else:
                 #print(" No Sell positions found.")
           #     
########################################################################################### بررسی شروط اولیه  #########################################################################################################
       
             """ current_datetime = datetime.now()
             LastCandle = FrameRatesM1.iloc[-1]
             if (LastCandle['datetime'].hour in [0,1,9,10,11,12,13,16,17,22,23]) or (current_datetime.weekday() == 4 and current_datetime.hour >= 21) :
                Botdashboard(4 , self.Pair)
                return
             elif PublicVarible.CanOpenOrderST == False or PublicVarible.CanOpenOrder == False : 
                Botdashboard(36 , self.Pair)
                return
             
             BaseHigh = self.FindSwingHigh(FrameRatesM1, SymbolInfo.point,0,0,0)
             BaseLow = self.FindSwingLow(FrameRatesM1, SymbolInfo.point,0,0,0)
             if BaseHigh == 0 and BaseLow == 0 : 
                Botdashboard(27 , self.Pair)
                return
             if  SymbolInfo.spread < 4.99 or  SymbolInfo.spread > 20 : 
              Botdashboard(30 , self.Pair)
              return
             
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             
             RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 260)
             if RatesH1 is not None:
                   FrameRatesH1 = PD.DataFrame(RatesH1)
                   if not FrameRatesH1.empty:
                      FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                      FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                      FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)
                      SuperTH1 = supertrendH(Pair = self.Pair , high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], length= 10 , multiplier= 3) #SuperTrend calculation
                      DirectionH1 = SuperTH1.iloc[-2][1]
                      PriceST2 = SuperTH1.iloc[-2][0]
                      
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 260)
             if RatesM15 is not None:
                   FrameRatesM15 = PD.DataFrame(RatesM15)
                   if not FrameRatesM15.empty:
                      FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                      FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                      FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)
                      SuperT15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 14 , multiplier= 3) #SuperTrend calculation
                      DirectionM15 = SuperT15.iloc[-2][1]
                      PriceST3 = SuperT15.iloc[-2][0]
                      
                      if DirectionH1 == 1 : 
                         Botdashboard(22 , self.Pair)
                      else : Botdashboard(32 , self.Pair)
                      if DirectionM15 == 1 : 
                         Botdashboard(23 , self.Pair)
                      else : Botdashboard(13 , self.Pair)
                      if DirectionM15 != DirectionH1 : 
                         return
                      StochRSIM15 = PTA.stochrsi(close = FrameRatesM15['close'] , length = 10 , rsi_length= 10 , k= 3 , d= 3 ) 
                      StochRSI = StochRSIM15.iloc[-1][0]
                      #MFIH1 = PTA.mfi(high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], volume= FrameRatesH1['tick_volume'] , length = 14)    #MFI calculation
                      
                      STH30 = PTA.stoch(high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], k= 14, d= 5, smooth_k= 5)   #Stochastic calculation 
                      STH30slope = (STH30.iloc[-2][0] - STH30.iloc[-3][0]) 
                      
             #RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 25 )
             #if RatesM30 is not None:
             #      FrameRatesM30 = PD.DataFrame(RatesM30)
             #      if not FrameRatesM30.empty:
             #         FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
             #         FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
             #         FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)
             #         STH30 = PTA.stoch(high= FrameRatesM30['high'], low= FrameRatesM30['low'], close= FrameRatesM30['close'], k= 10, d= 1, smooth_k= 3)   #Stochastic calculation 
             #         #print(f"STH30.iloc[0][0] : {STH30.iloc[0][0]} and STH30.iloc[-1][0] : {STH30.iloc[-1][0]}")
             #         STH30slope = (STH30.iloc[-2][0] - STH30.iloc[-3][0])
             #         #print(f"{self.Pair} STH30slope : {STH30slope}") 
                      
########################################################################################### بررسی شروط اولیه بیش فروش و بیش خرید  #########################################################################################################
             
             if DirectionM15 == 1 and  STH30.iloc[-1][0] > 80 : 
                Botdashboard(12 , self.Pair) 
                return     
             #elif DirectionM15 == 1 and MFIH1.iloc[-1] > 90 : 
             #   Botdashboard(42 , self.Pair)
             #   return
             elif DirectionM15 == -1 and STH30.iloc[-1][0] < 20 :
                Botdashboard(12 , self.Pair) 
                return     
             #elif DirectionM15 == -1 and MFIH1.iloc[-1] < 10 : 
             #   Botdashboard(43 , self.Pair)
             #   return

########################################################################################### بدنه استراتژی  #########################################################################################################
             init ()
             BuyAllow = 1
             SellAllow = 1
             if SuperT15.iloc[-2][0] == SuperT15.iloc[-7][0] :
                BuyAllow = 0
                SellAllow = 0
                
             Levelprice = importantprice(self.Pair, PriceST2 , PriceST2) 
             if Levelprice == False :
                Botdashboard(37 , self.Pair)
                return
             ################################ شرط معامله فروش  #####################################

             if DirectionM15 == -1 and DirectionH1 == -1 :    
                sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
                
                BaseHigh = self.FindSwingHigh(FrameRatesM1, SymbolInfo.point,M5RSI,StochRSI_k2,RSIslope)  
                if BaseHigh == 0 : Botdashboard(20 , self.Pair)
                else : Botdashboard(33 , self.Pair)
                if  SymbolInfo.spread > 4.99 and  SymbolInfo.spread < 20 : Botdashboard(29 , self.Pair)
                else : Botdashboard(30 , self.Pair) 
                if M5RSI > 50 : Botdashboard(48 , self.Pair)
                else : Botdashboard(49 , self.Pair)
                if STH30slope < 0  : Botdashboard(59 , self.Pair)
                else : Botdashboard(61, self.Pair)
                if SellAllow == 1 : Botdashboard(63 , self.Pair)
                else : Botdashboard(64 , self.Pair)
                SymbolInfo = MT5.symbol_info(self.Pair)
                
                if (BaseLow == 0) and STH30slope < 0  and  M5RSI > 50  and SellAllow  and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :                                                                      write_None(self.Pair,text = "Base Not Found")
                if (BaseLow == -1 or BaseLow == -2 or BaseLow == -3 or BaseLow == -4 or BaseLow == -5) and STH30slope > 0 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :      write_None(self.Pair,text = "Stochastic M30 Slop Not +")     
                if (BaseLow == -1 or BaseLow == -2 or BaseLow == -3 or BaseLow == -4 or BaseLow == -5) and STH30slope < 0 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :      write_None(self.Pair,text = "M5 RSI is > 50 For buy") 
                if (BaseLow == -1 or BaseLow == -2 or BaseLow == -3 or BaseLow == -4 or BaseLow == -5) and STH30slope < 0 and SellAllow == 0 and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ): write_None(self.Pair,text = "M5 Supertrend Slop Not ok") 
                if (BaseLow == -1 or BaseLow == -2 or BaseLow == -3 or BaseLow == -4 or BaseLow == -5) and STH30slope < 0 and SellAllow and (SymbolInfo.spread < 4.99 or SymbolInfo.spread > 20 ) :      write_None(self.Pair,text = "Spread out of range") 
                
                if (BaseHigh == -1 or BaseHigh == -2 or BaseHigh == -3 or BaseHigh == -4 or BaseLow == -5)  and STH30slope < -1  and  StochRSI > 20  and SellAllow  and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :    #and M5RSI_Slop < 0######## شرط اصلی پیدا کردن نقطه ورود به معامله ##########   STH30slope < 0 and RSIslope < -0.5 and StochRSI_k2 > 80 
                   write_trade_info_to_file(self.Pair ,"Sell" , BaseHigh, STH30slope, StochRSI_k2, M5RSI , DirectionST1 , DirectionH1 , DirectionM15 )
                   EntryPrice = SymbolInfo.bid                                                        ######### قیمت  ورود به معامله ##########
                   Volume = self.CalcLotSize(Point= SymbolInfo.point)                                #########  محاسه حجم ورود به معامله ##########
                   SL = PriceST3 + (50 * SymbolInfo.point)                                            #########  تعیین حدضرر معامله #########
                   TP1 = EntryPrice - (SymbolInfo.spread * 3 * SymbolInfo.point) #(Pipprofit * SymbolInfo.point))                               #########  تعیین حدسود معامله ########## 
                   if TP1 > EntryPrice - ( 50 * SymbolInfo.point) : 
                      TP1 = EntryPrice - ( 50 * SymbolInfo.point)
                   print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                   Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                   OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"IRAN BanooBot{PublicVarible.Id} M{str(self.TimeFrame)}") #########  ارسال اطلاعات فروش به تابع  ########## 
                   

             ############################# شرط معامله خرید  #####################################
                      
             if DirectionM15 == 1 and DirectionH1 == 1 :     
                buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
                if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return
                BaseLow = self.FindSwingLow(FrameRatesM1, SymbolInfo.point,M5RSI,StochRSI_k2,RSIslope)
                if BaseLow == 0 : Botdashboard(28 , self.Pair)
                else :  Botdashboard(34 , self.Pair)
                if  SymbolInfo.spread > 4.99 and  SymbolInfo.spread < 20 : 
                     Botdashboard(29 , self.Pair)
                     #print("SymbolInfo.spread" , SymbolInfo.spread)
                else : Botdashboard(30 , self.Pair) 
                if M5RSI < 50 : Botdashboard(50 , self.Pair)
                else :  Botdashboard(51 , self.Pair)
                if STH30slope > 0  : Botdashboard(60 , self.Pair)
                else : Botdashboard(62, self.Pair)
                if BuyAllow == 1 : Botdashboard(63 , self.Pair)
                else : Botdashboard(64 , self.Pair)
                SymbolInfo = MT5.symbol_info(self.Pair)
                
                if (BaseLow == 0) and STH30slope > 0 and M5RSI < 50 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :                                                                      write_None(self.Pair,text = "Base Not Found")
                if (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and STH30slope < 0 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :      write_None(self.Pair,text = "Stochastic M30 Slop Not +")     
                if (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and STH30slope > 0 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :      write_None(self.Pair,text = "M5 RSI is > 50 For buy") 
                if (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and STH30slope > 0 and BuyAllow == 0 and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) : write_None(self.Pair,text = "M5 Supertrend Slop Not ok") 
                if (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and STH30slope > 0 and BuyAllow and (SymbolInfo.spread < 4.99 or SymbolInfo.spread > 20 ) :       write_None(self.Pair,text = "Spread out of range") 

                if (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and STH30slope > 1 and StochRSI < 80 and BuyAllow and (SymbolInfo.spread > 4.99 and SymbolInfo.spread < 20 ) :        #and M5RSI_Slop > 0######## شرط اصلی پیدا کردن نقطه ورود به معامله ########## (BaseLow == 1 or BaseLow == 2 or BaseLow == 3 or BaseLow == 4 or BaseLow == 5) and RSIslope > 0.5  and StochRSI_k2 < 20  
                   write_trade_info_to_file(self.Pair ,"Buy" , BaseLow, STH30slope, StochRSI_k2, M5RSI , DirectionST1 , DirectionH1 , DirectionM15 )
                   EntryPrice = SymbolInfo.ask                                                           ######### قیمت  ورود به معامله ##########
                   Volume = self.CalcLotSize(Point= SymbolInfo.point)                                    #########  محاسه حجم ورود به معامله ##########
                   if DirectionH1 == -1 : 
                      Volume = round(self.CalcLotSize(Point= SymbolInfo.point) / 2 , 2)                          #########  محاسه حجم ورود به معامله ##########
                   SL = PriceST3 - (50 * SymbolInfo.point)    
                   TP1 = EntryPrice + (SymbolInfo.spread * 3 * SymbolInfo.point) # (Pipprofit * SymbolInfo.point))                                   #########  تعیین حدسود معامله ##########
                   if TP1 > EntryPrice + ( 50 * SymbolInfo.point) : 
                      TP1 = EntryPrice + ( 50 * SymbolInfo.point) 
                   print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                   Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                   OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"IRAN BanooBot{PublicVarible.Id} M{str(self.TimeFrame)}") #########  ارسال اطلاعات فروش به تابع  ##########      
               
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
          H3 = FrameRates.iloc[-4]['high']
          L3 = FrameRates.iloc[-4]['low']
          H4 = FrameRates.iloc[-5]['high']
          L4 = FrameRates.iloc[-5]['low']
          H5 = FrameRates.iloc[-6]['high'] 
          Len1 = O1 - C1 

          if H3 < H2 > H1 and C1 < L2 and C1 < L3 : 
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #    PublicVarible.last_message_time = time.time()
             #    PromptToTelegram(f"الگوی سر و شانه نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Head and Shoulders pattern found ...")
             Base = -1 

          mean = (C1 - O1) * 0.65
          if (C1 < O1 and C2 > O2 and  H2 < H1 and L2 > L1 and C2 < O1 and O2 > C1 and O2 - C2 < mean ) : 
             #if time.time() - PublicVarible.last_message_time >= 10 :
             #   PublicVarible.last_message_time = time.time()
             #   PromptToTelegram(f"🔵الگوی پوشاننده نزولی پیدا کردم ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Engulfing pattern found ...")
             Base = -2  

          if ((C2 < O2 and H2 == O2 and (C2 - L2) > (O2 - C2) * 2 and O1 < H2 and C1 < O1 and C1 < L2) or (C2 > O2 and H2 == C2 and (O2 - L2) > (C2 - O2) * 2 and O1 < H2 and C1 < O1 and C1 < L2)) and (H3 < H2 > H1) :
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #   PublicVarible.last_message_time = time.time()
             #   PromptToTelegram(f"🔵الگوی مرد به دار آویخته نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Hunging man pattern found ...")
             Base = -3   

          if (C2 > O2 and C2 - O2 > 1 and O1 > C2 and C1 < O1 and C1 < (C2 + O2)/2)  and (H3 < H2 > H1) : 
              #if time.time() - PublicVarible.last_message_time >= 5 :
              #  PublicVarible.last_message_time = time.time()
              #  PromptToTelegram(f"🔵الگوی ابر سیاه پوشاننده نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
              print("Bearish Dark Cloud Cover pattern found ...")
              Base = -4   
              
          if  (C1 < O1 and (H1 - O1) > (O1 - C1) * 2 and (C1 - L1) * 2 < (O1 - C1))  and (H3 < H2 > H1) : 
              print("Bearish PinBar pattern found ...")
              Base = -5 
              
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
          H3 = FrameRates.iloc[-4]['high']
          L3 = FrameRates.iloc[-4]['low']
          H4 = FrameRates.iloc[-5]['high']
          L4 = FrameRates.iloc[-5]['low']
          L5 = FrameRates.iloc[-6]['low']

          if L3 > L2 < L1  and C1 > H2 and C1 > H3 : 
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #   PublicVarible.last_message_time = time.time()
             #   #PromptToTelegram(f"الگوی سر و شانه صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Head and Shoulders pattern found ...")
             Base = 1 

          mean = (C1 - O1) * 0.65
          if (C1 > O1 and C2 < O2 and H2 < H1 and L2 > L1 and O2 < C1 and C2 > O2 and O2 - C2 < mean)  :
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #   PublicVarible.last_message_time = time.time()
             #   PromptToTelegram(f"🔵الگوی پوشاننده صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Engulfing pattern found ...")
             Base = 2   

          if ((C2 < O2 and H2 == O2 and (C2 - L2) > (O2 - C2) * 2 and O1 > H2 and C1 > O1) or (C2 > O2 and H2 == C2 and (O2 - L2) > (C2 - O2) * 2 and O1 > H2 and C1 > O1))and (L3 > L2 < L1)  :
             #if time.time() - PublicVarible.last_message_time >= 5 :
             #   PublicVarible.last_message_time = time.time()
             #   PromptToTelegram(f"🔵الگوی چکش صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Hummer pattern found ...")
             Base = 3 
          
          if (C2 < O2 and O2 - C2 > 1 and C1 > O2 and C1 > O1 and C1 > (C2 + O2)/2) and (L3 > L2 < L1) : 
              #if time.time() - PublicVarible.last_message_time >= 5 :
              #  PublicVarible.last_message_time = time.time()
              #  PromptToTelegram(f"🔵الگوی فرفره صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M5RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
              print("Bullish Piercing pattern found ...")
              Base = 4  
              
          if  (C1 > O1 and (O1 - L1) > (C1 - O1) * 2 and (H1 - C1) * 2 < (C1 - O1)) and (L3 > L2 < L1) : 
              print("Bullish PinBar pattern found ...")
              Base = 5  
              
          return (Base)

########################################################################################################
      def CalcLotSize(self,Point):
        
          if self.Pair == 'XAUUSDb' : 
             Volume = GetBalance() // 300 * 0.01
          else :  Volume = GetBalance() // 150 * 0.01
         # print(" Volume: ",Volume)
          if  Volume < 0.01 : 
              Volume = 0.01
          return Volume
########################################################################################################
def CloseAllPosi(Pair:str):
     #MT5.Close(symbol= Pair)
   #  Prompt(f"Market trend is changed and All orders successfully closed, Balance: {str(GetBalance())}$")
   #  PromptToTelegram(Text= f"Market trend is changed and All orders successfully closed" + "\n" + f"💰 Balance: {str(GetBalance())}$")
     return True
########################################################################################################"""
