﻿#from math import floor
#from mimetypes import init
#from multiprocessing.pool import CLOSE
#from pickle import NONE
#from xmlrpc.client import DateTime
#from matplotlib.colors import Normalize
#import pandas_ta as PTA
import pandas as PD
#from scipy.signal import normalize
from Utility import *
from Trade import *
import PublicVarible
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
#import ta
#import numpy as np
from datetime import datetime


class SupplyDemandStrategyV1():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV1 M5 quick Spike --------------")
          CloseAllPosition(self.Pair)
          if PublicVarible.Quick_trade == False  : 
             print("Quick_trade Stoped By Manager ...  ")
             #return

          GreenPair  = ['CADJPYb' , 'EURCADb' , 'USDJPYb' , 'USDCHFb', 'EURCHFb' , 'AUDNZDb' , 'AUDUSDb' , 'CADCHFb' , 'DowJones30' , 'XAUUSDb' ]
          YellowPair	= ['AUDJPYb' , 'EURUSDb' , 'NZDUSDb' ]
          RedPair    = ['AUDCADb' , 'AUDCHFb' , 'EURGBPb' , 'NZDCADb' , 'EURAUDb' , 'USDCADb']			
          BlackPair	= ['GBPUSDb' , 'EURNZDb' , 'NZDCHFb' , 'EURJPYb']
          
          if PublicVarible.risk == 3 : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume = 0.02
             elif self.Pair in YellowPair : Volume = 0.01
             elif self.Pair in RedPair    : Volume = 0.00
             else : Volume = 0.01
          elif PublicVarible.risk == 2  : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume = 0.01
             elif self.Pair in YellowPair : Volume = 0.01
             elif self.Pair in RedPair    : Volume = 0.00
             else : Volume = 0.01
          elif PublicVarible.risk == 1 : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume = 0.01
             elif self.Pair in YellowPair : Volume = 0.00
             elif self.Pair in RedPair    : Volume = 0.00
             else : Volume = 0.00

          sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
          if sell_positions_with_open_prices:
            for ticket, open_price in sell_positions_with_open_prices.items():
              positions = MT5.positions_get()
              for position_info in positions:
               if position_info.symbol == self.Pair :
                  Botdashboard(54 , self.Pair)
                  return
               
          buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
          if buy_positions_with_open_prices:
             for ticket, open_price in buy_positions_with_open_prices.items():
                positions = MT5.positions_get()
                for position_info in positions:
                  if position_info.symbol == self.Pair :
                     Botdashboard(53 , self.Pair)
                     return 
                  
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
             
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 250)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty:
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)
                   
             RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 250)
             if RatesM30 is not None:
                FrameRatesM30 = PD.DataFrame(RatesM30)
                if not FrameRatesM30.empty:
                   FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
                   FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
                   FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)
########################################################################################### بررسی شروط اولیه  #########################################################################################################
             current_datetime = datetime.now()
             LastCandle = FrameRatesM5.iloc[-1]
             minutes_to_exclude = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
             if (LastCandle['datetime'].hour in [0,1]) or (current_datetime.weekday() == 4 and current_datetime.hour >= 23)  or current_datetime.minute not in minutes_to_exclude :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return
             if (current_datetime.hour >= 22 and current_datetime.minute == 0) or (current_datetime.weekday() == 4 and current_datetime.hour >= 17  and current_datetime.minute == 0) : 
                PublicVarible.CanOpenOrder = False  
             elif current_datetime.hour == 3 and current_datetime.minute == 0 :
                PublicVarible.CanOpenOrder = True  
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             #Bband = PTA.bbands(close= FrameRatesM15['close'] , length= 40 , std = 2 , ddof= 0 , mamode = 'EMA' )    
             #BRoof = round(Bband.iloc[-2][-3] , 2 ) 
             #BBase = round(Bband.iloc[-2][-5] , 2 )  

             SuperTM5 = supertrend(Pair = self.Pair , high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 10 , multiplier= 4) #SuperTrend calculation
             DirectionM5 = SuperTM5.iloc[-2][1]
             Direction = "UP" if DirectionM5 == 1 else "DOWN"
             PriceST3 = SuperTM5.iloc[-2][0]
             
             SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 10 , multiplier= 4) #SuperTrend calculation
             DirectionM15 = SuperTM15.iloc[-2][1]
             Direction15 = "UP" if DirectionM15 == 1 else "DOWN"
             PriceST1 = SuperTM15.iloc[-2][0]
             
             #SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM30['high'], low= FrameRatesM30['low'], close= FrameRatesM30['close'], length= 10 , multiplier= 3.5) #SuperTrend calculation
             #DirectionM15 = SuperTM15.iloc[-2][1]
             #Direction15 = "UP" if DirectionM15 == 1 else "DOWN"
             #PriceST1 = SuperTM15.iloc[-2][0]

             SuperTM15_2 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 9 , multiplier= 9) #SuperTrend calculation
             DirectionM15_2 = SuperTM15_2.iloc[-2][1]
             Direction15_2 = "UP" if DirectionM15_2 == 1 else "DOWN"
             PriceST2 = SuperTM15_2.iloc[-2][0]
             PriceST75= SuperTM15_2.iloc[-50][0]
             
             if PriceST2 == PriceST75 : 
                print(f"PriceST2 ==  PriceST50 and return")
                return
             
             C_old_O = FrameRatesM5.iloc[-2]['open']
             C_old_C = FrameRatesM5.iloc[-2]['close']
             C_old_H = FrameRatesM5.iloc[-2]['high']
             C_old_L = FrameRatesM5.iloc[-2]['low']

             C_P_old_O = FrameRatesM5.iloc[-3]['open']
             C_P_old_C = FrameRatesM5.iloc[-3]['close']
             C_P_old_H = FrameRatesM5.iloc[-3]['high']
             C_P_old_L = FrameRatesM5.iloc[-3]['low']
             
             D_Leg_point = (C_P_old_H - C_old_L) / (SymbolInfo.point)
             print("D_Leg_point",D_Leg_point)
             
             ## لگ نزولی سریع
             if C_old_O > C_old_C and C_P_old_O > C_P_old_C : 
               if C_old_H < C_P_old_H and C_old_L < C_P_old_L  : 
                  if (self.Pair == 'XAUUSDb'  and D_Leg_point > 200) or (self.Pair != 'XAUUSDb'  and (D_Leg_point) > 110)  : 
                    roof, floor, diff , message = get_pair_values(self.Pair)
                    if message is None or time.time() - message >= 280 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,0,0,0,last_message_time)
                      Text =  f"{self.Pair}\n"
                      if DirectionM5 == -1 and DirectionM15 == -1 and DirectionM15_2 == -1  : 
                         Text += f"Auto Trade Direct ... 🤖 \n"
                      else : f"Manual Trade ... 👨‍  \n"
                      if  DirectionM5 == -1 and DirectionM15 == -1 and DirectionM15_2 == -1 :
                            Text +=f"معامله : فروش / SELL  \n" 
                      else: Text +=f"نیاز به بررسی ...  \n" 
                      Text += f" لگ نزولی سریع ... 🔴 \n"
                      Text += f"M5 روند : {Direction}\n"
                      Text += f"M15روند : Up" if DirectionM15 == 1 else f"M15روند : Down"
                      PromptToTelegram(Text)
                      #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)

                    if PublicVarible.CanOpenOrder == False :  #PublicVarible.CanOpenOrderST == False or 
                      Botdashboard(36 , self.Pair)
                      return 
                    if PublicVarible.Quick_trade == False  : 
                       return      
                                
                    if DirectionM5 == -1 and DirectionM15 == -1 and DirectionM15_2 == -1  : 
                      EntryPrice = SymbolInfo.ask           
                      SL = PriceST1 + ( SymbolInfo.point * 50)                                                                               #########  تعیین حدضرر معامله #########
                      TP1 = EntryPrice - (abs(EntryPrice - SL) * 1 )   #SymbolInfo.ask - ( SymbolInfo.point * 100) 
                      write_trade_info_to_file(self.Pair ,"Down Leg" , D_Leg_point , 0, 0, 0 )
                      write_trade_info_to_file(self.Pair ,"Sell" , EntryPrice, SL, TP1, Direction )
                      print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V1 - M5")

             U_Leg_point = ((C_old_H - C_P_old_L) / (SymbolInfo.point))
             print("U_Leg_point" ,U_Leg_point)
             
             ##  لگ صعودی سریع
             if C_old_O < C_old_C and C_P_old_O < C_P_old_C : 
                if C_old_H > C_P_old_H and C_old_L > C_P_old_L  : 
                  if (self.Pair == 'XAUUSDb'  and U_Leg_point > 200) or (self.Pair != 'XAUUSDb'  and U_Leg_point > 110 )  : 
                    roof, floor, diff , message = get_pair_values(self.Pair)
                    if message is None or time.time() - message >= 280 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,0,0,0,last_message_time)
                      Text =  f"{self.Pair}\n"
                      if DirectionM5 == 1 and DirectionM15 == 1 and DirectionM15_2 == 1  : 
                         Text += f"Auto Trade Direct ... 🤖 \n"
                      else : f"Manual Trade ... 👨‍  \n"
                      if  DirectionM5 == 1 and DirectionM15 == 1 and DirectionM15_2 == 1 :
                            Text +=f"معامله : خرید / BUY  \n" 
                      else: Text +=f"نیاز به بررسی ...  \n" 
                      Text += f"لگ صعودی سریع... 🟢 \n"
                      Text += f"M5 روند : {Direction}\n"
                      Text += f"M15روند : Up \n" if DirectionM15 == 1 else f"M15روند : Down \n"
                      PromptToTelegram(Text)
                      #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)

                    if PublicVarible.CanOpenOrder == False :  #PublicVarible.CanOpenOrderST == False or 
                        Botdashboard(36 , self.Pair)
                        return
                    if PublicVarible.Quick_trade == False  : 
                       return      
                    
                    if DirectionM5 == 1 and DirectionM15 == 1 and DirectionM15_2 == 1 :
                       EntryPrice = SymbolInfo.bid 
                       SL = PriceST1 - ( SymbolInfo.point * 50)                                #########  تعیین حدضرر معامله #########
                       TP1 = (abs(EntryPrice - SL) * 1 ) + EntryPrice  #SymbolInfo.bid + ( SymbolInfo.point * 100)    
                       write_trade_info_to_file(self.Pair ,"Up Leg" , U_Leg_point , 0, 0, 0 )
                       write_trade_info_to_file(self.Pair ,"Buy" , EntryPrice, SL, TP1, Direction )
                       print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V1 - M5") 
                       
""""########################################################################################################
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
"""