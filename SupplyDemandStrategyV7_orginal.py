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
           
########################################################################################################
      def Main(self):
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
                   #ADX = PTA.trend.adx(high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 15)    #ADX calculation
                   
                   RatesM1 = MT5.copy_rates_from_pos(self.Pair, self.TimeFrame, 0, 160)
                   if RatesM1 is not None:
                      FrameRatesM1 = PD.DataFrame(RatesM1)
                      if not FrameRatesM1.empty:
                         FrameRatesM1['datetime'] = PD.to_datetime(FrameRatesM1['time'], unit='s')
                         FrameRatesM1 = FrameRatesM1.drop('time', axis=1)
                         FrameRatesM1 = FrameRatesM1.set_index(PD.DatetimeIndex(FrameRatesM1['datetime']), drop=True)
                         ATR = PTA.atr(high= FrameRatesM1['high'], low= FrameRatesM1['low'], close= FrameRatesM1['close'], length= 15)    #ATR calculation
                         #print("ATR.iloc[-1] = " , ATR.iloc[-1])
                         #print("Price = " , SymbolInfo.ask)
                         NormalATR = ATR.iloc[-1] / SymbolInfo.ask * 3000
                         #print("NormalATR = " ,"{:.10f}".format(NormalATR))
                         
                         RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 260)
                         if RatesH1 is not None:
                            FrameRatesH1 = PD.DataFrame(RatesH1)
                            if not FrameRatesH1.empty:
                               FrameRatesH1['datetime'] = PD.to_datetime(FrameRatesH1['time'], unit='s')
                               FrameRatesH1 = FrameRatesH1.drop('time', axis=1)
                               FrameRatesH1 = FrameRatesH1.set_index(PD.DatetimeIndex(FrameRatesH1['datetime']), drop=True)

                         SuperTH1 = supertrendH(Pair = self.Pair , high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], length= 10 , multiplier= 3) #SuperTrend calculation
                         DirectionH1 = SuperTH1.iloc[-2][1]
                         self.CalcLotSize(Point= SymbolInfo.point)
                        
                         if DirectionH1 == 1 : 
                            DirectionST2 = 1
                         elif DirectionH1 == -1 : 
                            DirectionST2 = -1
                         else : DirectionST2 = 0
                         PriceST2 = SuperTH1.iloc[-2][0]                         
                         
                         #if NormalATR >= 0.1 : 
                         ST1 = supertrend(Pair = self.Pair , high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 10 , multiplier= 3) #SuperTrend calculation
                         #else :
                         #      ST1 = supertrend(Pair = self.Pair , high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 10 , multiplier= 4.5) #SuperTrend calculation
                           
                         DirectionST1 = ST1.iloc[-2][1]
                         PriceST1 = ST1.iloc[-2][0]

                         StochRSI = PTA.stochrsi(close= FrameRatesM1['close'],length= 14, rsi_length= 14, k= 3, d= 3)                                       #StochRSI calculation
                         StochRSI_k2 = StochRSI.iloc[-1][0]
                         #print(" StochRSI_k2 : ",round(StochRSI_k2 , 2))

                         RSI = PTA.rsi(close= FrameRatesM1['close'], length= 7)    #RSI calculation
                         M1RSI = RSI.iloc[-1]
                         #print(" M1 RSI      : ",round(RSI.iloc[-1] , 2))

                         RSIslope = (RSI.iloc[-1] - RSI.iloc[-7]) / 7 
                         #print(f" RSIslope (1-7) : {round(RSIslope , 2)} D and M1RSI : {round(M1RSI , 2)}")
                         ############################### position Modify ################################################

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
                                       if SymbolInfo.ask >= abs(abs(entry_price - take_profit)*0.75 + entry_price):
                                           # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                           new_stop_loss = (entry_price + take_profit) / 2
                                           # اعمال تغییرات
                                           ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                           print(" Buy Position Tp and Sl Modified to Bearish Status")
                                       else:
                                           print(f" Condition not met for ticket                             {ticket}" , "\n")

                                       if M1RSI > 90 :
                                          MT5.Close(symbol= self.Pair)
                                          PromptToTelegram(Text= f"{self.Pair} ❎ Buy Posision successfully closed by RSI Contoroler (>90)" + "\n" + f"💰 Balance: {str(GetBalance())}$")
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
                                       if SymbolInfo.bid <= abs(abs(entry_price - take_profit)*0.75 - entry_price):
                                           # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                           new_stop_loss = (entry_price + take_profit) / 2
                                           # اعمال تغییرات
                                           ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                           print(" Sell Position Tp and Sl Modified to Bearish Status")
                                       else:
                                           print(f" Condition not met for ticket                             {ticket}" , "\n")
                                       
                                       if M1RSI < 5 :
                                          MT5.Close(symbol= self.Pair)
                                          PromptToTelegram(Text= f"{self.Pair} ❎ Sell Posision successfully closed by RSI Contoroler (<10)" + "\n" + f"💰 Balance: {str(GetBalance())}$")
                         #else:
                             #print(" No Sell positions found.")

                          ################################################################################################

                         LastCandle = FrameRatesM1.iloc[-1]
                         #if LastCandle['datetime'].hour == 2 : PublicVarible.CanOpenOrderST = True
                         Levelprice = importantprice(self.Pair, PriceST2 , PriceST2) #,PriceST3
                         if Levelprice == False :
                            Botdashboard(37 , self.Pair)
                            return
                         
                         if PublicVarible.CanOpenOrderST == False or PublicVarible.CanOpenOrder == False : 
                            Botdashboard(36 , self.Pair)
                            return
                         if NormalATR < 0.1 : 
                            Botdashboard(5 , self.Pair)
                            return
                         elif LastCandle['datetime'].hour in [0] :
                              Botdashboard(4 , self.Pair)
                              return
                         elif PublicVarible.CanOpenOrder and Levelprice :
                            #Botdashboard(6 , self.Pair)
                            #Botdashboard(7 , self.Pair)
                            #Botdashboard(35 , self.Pair)
                            RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 16 )
                            if RatesM30 is not None:
                               FrameRatesM30 = PD.DataFrame(RatesM30)
                            if not FrameRatesM30.empty:
                               FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
                               FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
                               FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)
                               STH30 = PTA.stoch(high= FrameRatesM30['high'], low= FrameRatesM30['low'], close= FrameRatesM30['close'], k= 10, d= 1, smooth_k= 3)   #Stochastic calculation 
                               if STH30.iloc[-1][0] < 20 :
                                  Botdashboard(11 , self.Pair)
                                  #return
                               if STH30.iloc[-1][0] > 80 :
                                  Botdashboard(12 , self.Pair) 
                                  #return
                                  #print("STH30.iloc[-1][0] : " , STH30.iloc[-1][0])
                               
                            MFIH1 = PTA.mfi(high= FrameRatesH1['high'], low= FrameRatesH1['low'], close= FrameRatesH1['close'], volume= FrameRatesH1['tick_volume'] , length = 14)    #MFI calculation

                            if MFIH1.iloc[-1] > 80 : 
                               #PublicVarible.MFIover = 1
                               Botdashboard(42 , self.Pair)
                               #return
                               #print("MFIH1.iloc[-1] : " , MFIH1.iloc[-1])
                            elif MFIH1.iloc[-1] < 20 : 
                               #PublicVarible.MFIover = -1 
                               Botdashboard(43 , self.Pair)
                               #return
                            
                            Pipprofit = round(NormalATR * 150, 0)       #Point Profit 
                            if Pipprofit < 100: 
                                Pipprofit = 100
                            elif Pipprofit > 200:
                                Pipprofit = 200 
                            if (DirectionST1 == -1 and DirectionST2 == 1) or (DirectionST1 == 1 and DirectionST2 == -1) :
                                Pipprofit = 100
                            Piploss = round(NormalATR * 200 , 0) * 10      #Point Loss
                            if Piploss < 200 : 
                                Piploss = 200
                            elif Piploss > 400:
                                Piploss = 400 
                            if self.Pair == 'XAUUSDb' :
                                Piploss = 600
                           ##################   ################
                            init ()
                            #all_positions = MT5.positions_get()
                            #total_loss_dollar = 0.0  # متغیر برای نگهداری مجموع ضرر دلاری
                            #for position in all_positions:
                            #   #if position.type == MT5.POSITION_TYPE_BUY:
                            #    entry_price = position.price_open
                            #    stop_loss = position.sl
                            #    volume = position.volume
                            #    # محاسبه فاصله قیمت ورود تا حد ضرر
                            #    price_distance = abs(entry_price - stop_loss)
                            #    # محاسبه ضرر دلاری معامله
                            #    trade_loss = price_distance * volume * 100
                            #    # اضافه کردن ضرر معامله به مجموع ضررها
                            #    total_loss_dollar += trade_loss
                            #Balance = GetBalance()
                            #current_datetime = datetime.now()
                            #TodayProfit = ProfitByDay(current_datetime)
                            #if TodayProfit < Balance * -0.2 : Botdashboard(52 , self.Pair)
                            #if (total_loss_dollar) > (Balance * 0.1) : Botdashboard(53 , self.Pair)

                           ##################   ################
                                      

                           ##################  Market  ################  

                            if True : #(total_loss_dollar) < (Balance * 0.1)  and  TodayProfit > Balance * -0.2 :   ### بررسی میزان ریسک معاملات باز  and   بررسی میزان سود یا زیان امروز ###     
                                
                                #sell_positions_with_open_prices = get_sell_positions_with_open_prices()
                                #if sell_positions_with_open_prices:
                                #  for ticket, open_price in sell_positions_with_open_prices.items():
                                #    positions = MT5.positions_get()
                                #    for position_info in positions:
                                #     if position_info.symbol == self.Pair :
                                #        Botdashboard(54 , self.Pair)
                                #        return
                                #
                                if STH30.iloc[-1][0] > 20 and MFIH1.iloc[-1] > 20 :    
                                  if DirectionST1 == -1 : 
                                     BaseHigh = self.FindSwingHigh(FrameRatesM1, SymbolInfo.point,M1RSI,StochRSI_k2,RSIslope)  
                                     Botdashboard(13 , self.Pair)
                                     #if A[7] >= MaxSellVol :
                                     #   Botdashboard(14 , self.Pair)
                                     #else : Botdashboard(15 , self.Pair)
                                     if CheckOrderIsOpen(self.Pair, LastCandle, self.TimeFrame, MT5.ORDER_TYPE_SELL, 20) == True:
                                        Botdashboard(16 , self.Pair)
                                     else : 
                                        #Botdashboard(17 , self.Pair)
                                        if BaseHigh == 0 : Botdashboard(20 , self.Pair)
                                        else : Botdashboard(33 , self.Pair)
                                        if StochRSI_k2 > 70 : Botdashboard(18 , self.Pair)
                                        else : Botdashboard(19 , self.Pair) 
                                        if M1RSI > 20 : Botdashboard(48 , self.Pair)
                                        else : Botdashboard(49 , self.Pair)
                                        if RSIslope < -0.5  : Botdashboard(55 , self.Pair)
                                        else : Botdashboard(56 , self.Pair)

                                        if BaseHigh == -1 and StochRSI_k2 > 70 and  RSIslope < -0.5 and M1RSI > 40 :    ######### شرط اصلی پیدا کردن نقطه ورود به معامله ########## and A[7] < MaxSellVol SellPrice == True and
                                           EntryPrice = SymbolInfo.bid
                                           Volume = self.CalcLotSize(Point= SymbolInfo.point)
                                           if DirectionST2 == 1 or DirectionST2 == 0 : 
                                              Volume = round(Volume * 0.6, 2)
                                           if Volume < 0.01 : Volume = 0.01
                                           if ATR.iloc[-1] > 0.55 : 
                                              if Volume > 0.01 : Volume = round(Volume * 0.8, 2)
                                              else : Volume = 0.01 

                                           SL = EntryPrice + (Piploss * SymbolInfo.point)    
                                           TP1 = (EntryPrice - (Pipprofit * SymbolInfo.point)) 
                                            
                                           print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                           Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                           OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"IRAN BanooBot{PublicVarible.Id} M{str(self.TimeFrame)}")


                                buy_positions_with_open_prices = get_buy_positions_with_open_prices()
                                if buy_positions_with_open_prices:
                                 for ticket, open_price in buy_positions_with_open_prices.items():
                                   positions = MT5.positions_get()
                                   for position_info in positions:
                                     if position_info.symbol == self.Pair :
                                        Botdashboard(53 , self.Pair)
                                        return
                                    
                                if STH30.iloc[-1][0] < 80 and MFIH1.iloc[-1] < 80 :     #MFIBuysignal  == 1 :  ##########  بررسی شرایط معامله خرید  ##########                                                                                                         #Market no Direction
                                  if DirectionST1 == 1 :                              ##########   بررسی شرط صعودی بودن روند بازار در چارت 5 دقیقه ای   ##########
                                     BaseLow = self.FindSwingLow(FrameRatesM1, SymbolInfo.point,M1RSI,StochRSI_k2,RSIslope)
                                     Botdashboard(23 , self.Pair) 
                                     #if A[6] >= MaxBuyVol : 
                                     #   Botdashboard(24 , self.Pair)
                                     #else : Botdashboard(25 , self.Pair)

                                     if CheckOrderIsOpen(self.Pair, LastCandle, self.TimeFrame, MT5.ORDER_TYPE_BUY, 15) == True:
                                        Botdashboard(26 , self.Pair)
                                     else : 
                                        #Botdashboard(27 , self.Pair)
                                        if BaseLow == 0 : Botdashboard(28 , self.Pair)
                                        else :  Botdashboard(34 , self.Pair)
                                        if StochRSI_k2 < 30 : Botdashboard(29 , self.Pair)
                                        else : Botdashboard(30 , self.Pair) 
                                        if M1RSI < 80 : Botdashboard(50 , self.Pair)
                                        else :  Botdashboard(51 , self.Pair)
                                        if RSIslope > 0.5  : Botdashboard(57 , self.Pair)
                                        else : Botdashboard(58, self.Pair)

                                        if BaseLow == 1 and StochRSI_k2 < 30 and RSIslope > 0.5 and M1RSI < 60 : ########## شرط اصلی پیدا کردن نقطه ورود به معامله ##########   and A[6] < MaxBuyVol and BuyPrice == True
                                           EntryPrice = SymbolInfo.ask
                                           Volume = self.CalcLotSize(Point= SymbolInfo.point)
                                           if DirectionST2 == -1 or DirectionST2 == 0 : 
                                              Volume = round(Volume * 0.6, 2)
                                           if Volume < 0.01 : Volume = 0.01
                                           if ATR.iloc[-1] > 0.55 : 
                                             if Volume > 0.01 : Volume = round(Volume * 0.8, 2)
                                             else : Volume = 0.01 

                                           SL = EntryPrice - (Piploss * SymbolInfo.point)   
                                           TP1 = (EntryPrice + (Pipprofit * SymbolInfo.point))

                                           print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                           Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                           OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"IRAN BanooBot{PublicVarible.Id} M{str(self.TimeFrame)}")
                                           #PublicVarible.LastBuyPrice = SymbolInfo.ask

########################################################################################################
      def FindSwingHigh(self, FrameRates, Point,M1RSI,StochRSI_k2,RSIslope):
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
          #if H5 < H4 and H4 < H3 and H3 > H2 and H2 > H1 and (C1 < L2 and C1 < L3 and C1 < L4) : 
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"الگوی سر و شانه نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Head and Shoulders pattern found ...")
             Base = -1 #Bearish Head and Shoulders pattern 

          mean = (C1 - O1) * 0.65
          if C1 < O1 and C2 > O2 and  H2 < H1 and L2 > L1 and C2 < O1 and O2 > C1 and O2 - C2 < mean : 
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی پوشاننده نزولی پیدا کردم ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Engulfing pattern found ...")
             Base = -2   #Bearish Engulfing pattern found ...

          if (C2 < O2 and H2 == O2 and (C2 - L2) > (O2 - C2) * 2 and O1 < H2 and C1 < O1 and C1 < L2) or (C2 > O2 and H2 == C2 and (O2 - L2) > (C2 - O2) * 2 and O1 < H2 and C1 < O1 and C1 < L2) :
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی مرد به دار آویخته نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bearish Hunging man pattern found ...")
             Base = -3    #Bearish Hunging man pattern found ...

          if C2 > O2 and C2 - O2 > 1 and O1 > C2 and C1 < O1 and C1 < (C2 + O2)/2 : 
              if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی ابر سیاه پوشاننده نزولی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)}  مقدار استوک {round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
              print("Bearish Dark Cloud Cover pattern found ...")
              Base = -4    #Bearish Dark Cloud Cover pattern found ...

          return (Base)

########################################################################################################
      def FindSwingLow(self, FrameRates, Point,M1RSI,StochRSI_k2,RSIslope):
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
          #if L5 > L4 and L4 > L3 and L3 < L2 and L2 < L1 and (C1 > H2 and C1 > H3 and C1 > H4): 
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"الگوی سر و شانه صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Head and Shoulders pattern found ...")
             Base = 1 #Bullish Head and Shoulders pattern 

          mean = (C1 - O1) * 0.65
          if C1 > O1 and C2 < O2 and H2 < H1 and L2 > L1 and O2 < C1 and C2 > O2 and O2 - C2 < mean :
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی پوشاننده صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Engulfing pattern found ...")
             Base = 2    #Bullish Engulfing pattern found ...

          if (C2 < O2 and H2 == O2 and (C2 - L2) > (O2 - C2) * 2 and O1 > H2 and C1 > O1) or (C2 > O2 and H2 == C2 and (O2 - L2) > (C2 - O2) * 2 and O1 > H2 and C1 > O1) :
             if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی چکش صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
             print("Bullish Hummer pattern found ...")
             Base = 3    #Bullish Hummer pattern found ...
          
          if C2 < O2 and O2 - C2 > 1 and C1 > O2 and C1 > O1 and C1 > (C2 + O2)/2 : 
              if time.time() - PublicVarible.last_message_time >= 300 :
                PublicVarible.last_message_time = time.time()
                PromptToTelegram(f"🔵الگوی فرفره صعودی پیدا کردم  ...{SymbolInfo.name} مقدار RSI : {round(M1RSI,2)} مقدار استوک :{round(StochRSI_k2,2)} شیب خط RSI: {round(RSIslope,2)} ")
              print("Bullish Piercing pattern found ...")
              Base = 4    #Bullish Piercing pattern found ...
          return (Base)

########################################################################################################
      def CalcLotSize(self,Point):
        
          if self.Pair == 'XAUUSDb' : 
             Volume = GetBalance() // 200 * 0.01
          else :  Volume = GetBalance() // 150 * 0.01
         # print(" Volume: ",Volume)
          return Volume
########################################################################################################
def CloseAllPosi(Pair:str):
     #MT5.Close(symbol= Pair)
   #  Prompt(f"Market trend is changed and All orders successfully closed, Balance: {str(GetBalance())}$")
   #  PromptToTelegram(Text= f"Market trend is changed and All orders successfully closed" + "\n" + f"💰 Balance: {str(GetBalance())}$")
     return True
########################################################################################################
