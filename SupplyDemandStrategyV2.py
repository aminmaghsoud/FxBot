﻿#from math import floor
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
#import PublicVarible
import time
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
#import ta
#import numpy as np
#from datetime import datetime


class SupplyDemandStrategyV2():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV2 M5 Spike --------------")
          """CloseAllPosition(self.Pair)
          
          GreenPair  = ['EURUSDb' , 'EURCHFb' , 'EURCADb' , 'EURGBPb' , 'USDCHFb' ,'USDJPYb' ]
          YellowPair	= ['AUDCADb' , 'NZDUSDb' , 'AUDNZDb' , 'EURAUDb' , 'CADJPYb' ,  'AUDUSDb'] 
          RedPair    = ['XAUUSDb' ,'GBPUSDb' , 'USDCADb' , 'NZDCADb' , 'CADCHFb' , 'AUDCHFb' , 'EURJPYb', 'AUDJPYb']
          BlackPair	= ['NZDCHFb', 'EURNZDb'  , 'DowJones30' ]					

          Volume = CalcLotSize()
          if PublicVarible.risk == 3 : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume *= 1.2
             elif self.Pair in YellowPair : Volume *= 1
             elif self.Pair in RedPair    : Volume *= 0.8
             else : Volume = 0.01
          elif PublicVarible.risk == 2  : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume *= 1
             elif self.Pair in YellowPair : Volume *= 0.8
             elif self.Pair in RedPair    : Volume *= 0.5
             else : Volume = 0.01
          elif PublicVarible.risk == 1 : 
             if   self.Pair in BlackPair  : return
             elif self.Pair in GreenPair  : Volume *= 0.8
             elif self.Pair in YellowPair : Volume *= 0.5
             elif self.Pair in RedPair    : Volume *= 0.3
             else : Volume = 0.01
          
          Volume = round(Volume , 2)
          print(f"Vloume = {Volume}")
          
          
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
                  """
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
                   
             
########################################################################################### بررسی شروط اولیه  #########################################################################################################
             """current_datetime = datetime.now()
             LastCandle = FrameRatesM15.iloc[-1]
             minutes_to_exclude = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

             if (LastCandle['datetime'].hour in [0 , 1]) or ((current_datetime.weekday() == 4 and current_datetime.hour > 20)) : #or (current_datetime.minute not in minutes_to_exclude ) :#or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return
             if ((current_datetime.hour > 20 and current_datetime.minute == 0)) : # or ((current_datetime.weekday() == 4 and current_datetime.hour >= 21  and current_datetime.minute == 0)) : 
                PublicVarible.CanOpenOrder = False  
             if current_datetime.hour == 2 and current_datetime.minute in minutes_to_exclude :
                PublicVarible.CanOpenOrder = False  """
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             adx = PTA.adx( high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 14 )
             adx_Signal = adx.iloc[-2][0]
             if adx_Signal < 21 : 
                print(f"ADX is : {adx_Signal}")
                return       
             
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

             print(f"Senkou Span A (Last): {senkou_a}")  
             print(f"Senkou Span B (Last): {senkou_b}") 
             print(f"Senkou Color: {Color_ichi}") 

             SuperTM15_2 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 9 , multiplier= 9) #SuperTrend calculation
             DirectionM15_2 = SuperTM15_2.iloc[-2][1]
             Direction15_2 = "UP" if DirectionM15_2 == 1 else "DOWN"
             PriceST2 = SuperTM15_2.iloc[-2][0]
             PriceST50= SuperTM15_2.iloc[-50][0]
             if PriceST2 == PriceST50 : 
                print(f"PriceST2 ==  PriceST50 and return ")
                return

             SuperTM5 = supertrend(Pair = self.Pair , high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionM5 = SuperTM5.iloc[-2][1]
             Direction = "UP" if DirectionM5 == 1 else "DOWN"
             PriceST3 = SuperTM5.iloc[-2][0]
             
             SuperTM15 = supertrend(Pair = self.Pair , high= FrameRatesM15['high'], low= FrameRatesM15['low'], close= FrameRatesM15['close'], length= 14 , multiplier= 4) #SuperTrend calculation
             DirectionM15 = SuperTM15.iloc[-2][1]
             Direction15 = "Green" if DirectionM15 == 1 else "Red"
             PriceST1 = SuperTM15.iloc[-2][0]
             print("SupertT Color : ",Direction15)

             cci = PTA.cci(high= FrameRatesM15['high'] , low= FrameRatesM15['low'], close= FrameRatesM15['close'],  length= 14  )
             cci_Signal = cci.iloc[-1]

             if DirectionM5 == 1 and DirectionM15 == 1 and DirectionM15_2 == 1 and cci_Signal > 150 : 
                print(f"cci is big  {cci_Signal}")
                #return  
             if DirectionM5 == -1 and DirectionM15 == -1 and DirectionM15_2 == -1 and cci_Signal < -150 : 
                print(f"cci is Small  {cci_Signal}")
                #return  

             if Direction_ichi == 1 and DirectionM5 == 1 and DirectionM15 == 1 :
                Market_Direction = 1
             elif Direction_ichi == -1 and DirectionM5 == -1 and DirectionM15 == -1 :
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
             if (FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high']) : #and (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low'])   :  #سختگیری بزرگ 
               #for initial_index in range(-7, -3) :
                 #current_index = initial_index  
                 #if count == 1 : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H : #and Now_c_L < Old_c_L : 
                          count += 1 
                          current_index -= 1
                       else : 
                           break
                 #else : 
                     # break
                 
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['low'] - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 300) or (self.Pair != 'XAUUSDb'and high_low_diff < 200)) :
                   return
                if  ((self.Pair == 'XAUUSDb'and high_low_diff > 800) or (self.Pair != 'XAUUSDb'and high_low_diff > 600)) :
                   return
                
                if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] : Basefloor = FrameRatesM5.iloc[-2]['low'] 
                else : Basefloor = FrameRatesM5.iloc[-3]['low']
                Baseroof = FrameRatesM5.iloc[-2]['high']
                print(f"Down high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof) / (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.5 ):
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      if Market_Direction == 1 : 
                         Text += f"Auto Trade Cross ... 🤖 \n" 
                      elif Market_Direction == -1  : 
                         Text += f"Auto Trade Direct ... 🤖 \n"
                      if Market_Direction == 1  :
                         Text += f"معامله : خرید (مدیریت شود) / BUY \n" 
                      elif Market_Direction == -1 :
                            Text +=f"معامله : فروش (مدیریت شود) / SELL  \n" 
                      else : Text += f" روندها غیر همجهت \n" 
                      Text += f" M5 لگ نزولی ... 🔴 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"ارتفاع رنج: {round(abs(Basefloor - Baseroof) / (SymbolInfo.point) /10 , 2)} pip \n"
                      Text += f"ظرفیت سود: {round((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) )/10 , 2)} pip \n"
                      Text += f"تعداد کندل: {count}\n"
                      #Text += f"ADX: {round(adx_Signal , 2)}\n"
                      #Text += f"CCI: {round(cci_Signal , 2)}\n"
                      if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      else : Text += f"روند مارکت : No Direc..."  
                      PromptToTelegram(Text)
                      #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)
                      
                   """if Market_Direction == -1 and cci_Signal > 90  : 
                      
                      EntryPrice = SymbolInfo.ask                                                                                        ######### قیمت  ورود به معامله ##########
                      SL = PriceST1 + ( SymbolInfo.point * 50)                                                                               #########  تعیین حدضرر معامله #########
                      Balance = GetBalance()
                      if ((abs(SL - EntryPrice) / SymbolInfo.point) * Volume) >  (Balance * 0.02) : 
                          Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2)   
                          #Volume = round(Volume / 3 , 2)
                          if Volume < 0.01 : Volume = 0.01
                      TP1 = EntryPrice - (abs(EntryPrice - SL) * 1.1 )   #SymbolInfo.ask - ( SymbolInfo.point * 100)    
                      write_trade_info_to_file(self.Pair ,"Sell" , EntryPrice, SL, TP1, Direction )
                      print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V2 - M5")

                   if Market_Direction == 1 and cci_Signal < 90 : 
                      
                      EntryPrice = SymbolInfo.bid                                                                                        ######### قیمت  ورود به معامله ##########
                      SL = PriceST1 - ( SymbolInfo.point * 50)    #########  تعیین حدضرر معامله #########
                      Balance = GetBalance()
                      if ((abs(SL - EntryPrice) / SymbolInfo.point) * Volume) >  (Balance * 0.02) : 
                          Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2)   
                          #Volume = round(Volume / 3 , 2)
                          if Volume < 0.01 : Volume = 0.01
                      TP1 = (abs(EntryPrice - SL) * 1.1 ) + EntryPrice  #SymbolInfo.bid + ( SymbolInfo.point * 100)    
                      write_trade_info_to_file(self.Pair ,"Buy" , EntryPrice, SL, TP1, Direction )
                      print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                      OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5")"""


             ## لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None       
             if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low']  :#and FrameRatesM5.iloc[-2]['high'] < FrameRatesM5.iloc[-3]['high']  : #سختگیری بزرگ 
               #for initial_index in range(-7, -3) :
                # current_index = initial_index  
                # if count == 1 :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if  Now_c_L > Old_c_L : #and Now_c_H > Old_c_H : 
                          count += 1 
                          current_index -= 1
                       else : 
                           break
                # else : 
                   # break
                 
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 300) or (self.Pair != 'XAUUSDb'and high_low_diff < 200)) :
                   return
                if  ((self.Pair == 'XAUUSDb'and high_low_diff > 800) or (self.Pair != 'XAUUSDb'and high_low_diff > 600)) :
                   return
                
                if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high'] : Baseroof = FrameRatesM5.iloc[-2]['high']  
                else : Baseroof = FrameRatesM5.iloc[-3]['high'] 
                Basefloor = FrameRatesM5.iloc[-2]['low']
                print(f"Up high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof)/ (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.50 ) : 
                   roof, floor, diff , message = get_pair_values(self.Pair)
                   if message is None or time.time() - message >= 300 :
                      last_message_time = time.time()
                      DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff,last_message_time)
                      Text =  f"{self.Pair}\n"
                      if Market_Direction == 1 : 
                         Text += f"Auto Trade Cross ... 🤖 \n" 
                      elif Market_Direction == -1  : 
                         Text += f"Auto Trade Direct ... 🤖 \n"
                      if Market_Direction == 1  :
                         Text += f"معامله : خرید (مدیریت شود) / BUY \n" 
                      elif Market_Direction == -1 :
                            Text +=f"معامله : فروش (مدیریت شود) / SELL  \n"  
                      else : Text += f" روندها غیر همجهت \n" 
                      Text += f"M5 لگ صعودی ... 🟢 \n"
                      Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                      Text += f"ارتفاع رنج: {round(abs(Basefloor - Baseroof) / (SymbolInfo.point) /10 , 2)} pip \n"
                      Text += f"ظرفیت سود: {round((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) )/10 , 2)} pip \n"
                      Text += f"تعداد کندل: {count}\n"
                      #Text += f"ADX: {round(adx_Signal , 2)}\n"
                      #Text += f"CCI: {round(cci_Signal , 2)}\n"
                      if    Market_Direction == 1 : Text += f"روند مارکت : Up"  
                      elif  Market_Direction == -1 : Text += f"روند مارکت : Down"  
                      else : Text += f"روند مارکت : No Direc..."  
                      PromptToTelegram(Text)
                      #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)
                   
                   """if Market_Direction == -1 and cci_Signal > -90 :
                       EntryPrice = SymbolInfo.ask                                                                                        ######### قیمت  ورود به معامله ##########
                       SL = PriceST1 + ( SymbolInfo.point * 50)                                                                               #########  تعیین حدضرر معامله #########
                       Balance = GetBalance()
                       if ((abs(SL - EntryPrice) / SymbolInfo.point) * Volume) >  (Balance * 0.02) : 
                          Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2)   
                          #Volume = round(Volume / 3 , 2)
                          if Volume < 0.01 : Volume = 0.01
                       TP1 = EntryPrice - (abs(EntryPrice - SL) * 1.1 )   #SymbolInfo.ask - ( SymbolInfo.point * 100)    
                       write_trade_info_to_file(self.Pair ,"Sell" , EntryPrice, SL, TP1, Direction )
                       print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V2 - M5")
       
                   if Market_Direction == 1 and cci_Signal < -90 :
                       EntryPrice = SymbolInfo.bid                                                                                        ######### قیمت  ورود به معامله ##########
                       SL = PriceST1 - ( SymbolInfo.point * 50)    #########  تعیین حدضرر معامله #########
                       Balance = GetBalance()
                       if ((abs(SL - EntryPrice) / SymbolInfo.point) * Volume) >  (Balance * 0.02) : 
                          Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2)   
                          #Volume = round(Volume / 3 , 2)
                          if Volume < 0.01 : Volume = 0.01
                       TP1 = (abs(EntryPrice - SL) * 1.1 ) + EntryPrice  #SymbolInfo.bid + ( SymbolInfo.point * 100)    
                       write_trade_info_to_file(self.Pair ,"Buy" , EntryPrice, SL, TP1, Direction )
                       print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V2 - M5") """
                       
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500