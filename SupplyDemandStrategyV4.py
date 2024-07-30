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
          #if self.Pair != "XAUUSDb":
          #   return
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
             current_datetime = datetime.now()
             LastCandle = FrameRatesM5.iloc[-1]
             minutes_to_exclude = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
             if (LastCandle['datetime'].hour in [0,1]) or (current_datetime.weekday() == 4 and current_datetime.hour >= 17) or current_datetime.minute not in minutes_to_exclude or current_datetime.second > 20  : 
                Botdashboard(4 , self.Pair)
                return
             
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 260)
             if RatesM5 is not None:
                   FrameRatesM5 = PD.DataFrame(RatesM5)
                   if not FrameRatesM5.empty:
                      FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                      FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                      FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
             SuperTM5 = supertrend(Pair = self.Pair , high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 14 , multiplier= 3) #SuperTrend calculation
             DirectionM5 = SuperTM5.iloc[-2][1]
             Direction = "UP" if DirectionM5 == 1 else "DOWN"
             PriceST3 = SuperTM5.iloc[-2][0]
             
             ## لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             high_low_diff = 0.0
             Basefloor = 0.0
             Baseroof = 0.0
             Text = None
             if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high']  : 
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
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['low'] - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 250) or (self.Pair != 'XAUUSDb'and high_low_diff < 150)) :
                   return
                if FrameRatesM5.iloc[-2]['low'] < FrameRatesM5.iloc[-3]['low'] : Basefloor = FrameRatesM5.iloc[-2]['low'] 
                else : Basefloor = FrameRatesM5.iloc[-3]['low']
                Baseroof = FrameRatesM5.iloc[-2]['high']
                print(f"high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof) / (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.5 ):
                 if True : #time.time() - PublicVarible.last_message_time >= 1 :
                    PublicVarible.last_message_time = time.time()
                    Text =  f"{self.Pair}\n"
                    Text += f"Auto Trade ... 🤖 \n" if Direction == "UP" else  f"Manual Trade ... 👨‍  \n"
                    Text += f"معامله : خرید / BUY \n" if Direction == "UP" else  f"معامله : فروش / SELL  \n"
                    Text += f"لگ نزولی ... 🔴 \n"
                    Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                    Text += f"ارتفاع رنج: {round(abs(Basefloor - Baseroof) / (SymbolInfo.point) /10 , 2)} pip \n"
                    Text += f"ظرفیت سود: {round((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) )/10 , 2)} pip \n"
                    Text += f"تعداد کندل: {count}\n"
                    Text += f"سقف: {Baseroof}\n"
                    Text += f"کف: {Basefloor}\n"
                    Text += f"M5 روند : {Direction}\n"
                    PromptToTelegram(Text)
                    #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)
                    DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff)

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
                       
                       if  Now_c_L > Old_c_L : #and Now_c_H > Old_c_H : 
                          count += 1 
                          current_index -= 1
                       else : 
                           break
             if count > 1 : 
                high_low_diff = round((abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
                if  ((self.Pair == 'XAUUSDb'and high_low_diff < 250) or (self.Pair != 'XAUUSDb'and high_low_diff < 150)) :
                    return
                if FrameRatesM5.iloc[-2]['high'] > FrameRatesM5.iloc[-3]['high'] : Baseroof = FrameRatesM5.iloc[-2]['high']  
                else : Baseroof = FrameRatesM5.iloc[-3]['high'] 
                Basefloor = FrameRatesM5.iloc[-2]['low']
                print(f"high_low_diff: {high_low_diff}  and  Baseroof: {Baseroof}  and  Basefloor: {Basefloor} and  Range arraye : {abs(Basefloor - Baseroof)/ (SymbolInfo.point)} \n")
                
                if (abs(Baseroof - Basefloor) / (SymbolInfo.point) < high_low_diff * 0.5 ) : 
                 if True : #time.time() - PublicVarible.last_message_time >= 1 :
                   PublicVarible.last_message_time = time.time()
                   Text =  f"{self.Pair}\n"
                   Text += f"Auto Trade ... 🤖 \n" if Direction == "DOWN" else  f"Manual Trade ... 👨‍  \n"
                   Text += f"معامله : خرید / BUY \n" if Direction == "UP" else  f"معامله : فروش / SELL \n"
                   Text += f"لگ صعودی ... 🟢 \n"
                   Text += f"ارتفاع لگ: {round(high_low_diff,2) / 10 } pip\n"
                   Text += f"ارتفاع رنج: {round(abs(Basefloor - Baseroof) / (SymbolInfo.point) /10 , 2)} pip \n"
                   Text += f"ظرفیت سود: {round((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) )/10 , 2)} pip \n"
                   Text += f"تعداد کندل: {count}\n"
                   Text += f"سقف: {Baseroof}\n"
                   Text += f"کف: {Basefloor}\n"
                   Text += f"M5 روند : {Direction}\n"
                   PromptToTelegram(Text)
                   #shape = draw_rectangle(self.Pair,Baseroof,Basefloor)
                   DBupdate = update_pair_values(self.Pair,Baseroof,Basefloor,high_low_diff)
                       

    
             roof, floor, diff = get_pair_values(self.Pair)
             if roof is not None and floor is not None and diff is not None:
                 
                 print(f"Pair: {self.Pair}, Roof: {roof}, Floor: {floor}, Diff: {diff}")
                 Ca1_o = FrameRatesM5.iloc[-1]['open']
                 Ca2_o = FrameRatesM5.iloc[-2]['open']
                 Ca3_o = FrameRatesM5.iloc[-3]['open']
                 Ca2_c = FrameRatesM5.iloc[-2]['close']
                 Ca3_c = FrameRatesM5.iloc[-3]['close']
                 


                 buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
                 if buy_positions_with_open_prices:
                    for ticket, open_price in buy_positions_with_open_prices.items():
                       positions = MT5.positions_get()
                       for position_info in positions:
                         if position_info.symbol == self.Pair :
                            Botdashboard(53 , self.Pair)
                            return
                 tt = (FrameRatesM5.iloc[-1]['open'] - roof ) / (SymbolInfo.point)
                 if Ca3_c > Ca3_o and Ca2_c > Ca2_o and Ca2_c > roof and tt < high_low_diff * 0.3 and Direction == "UP" : #Ca3_c > roof and
                   #if time.time() - PublicVarible.last_message_time >= 2 :
                       #PublicVarible.last_message_time = time.time() 
                       Text = f"🔺🔺 سیگنال خرید {self.Pair} 🔺🔺"
                       PromptToTelegram(Text)
                       EntryPrice = SymbolInfo.bid                                                                                        ######### قیمت  ورود به معامله ##########
                       if self.Pair == 'XAUUSDb' : Volume = 0.01
                       else:  Volume = 0.03                                                    #########  محاسه حجم ورود به معامله ##########
                       SL = floor - (20 * SymbolInfo.point)                                                                               #########  تعیین حدضرر معامله #########
                       TP1 = floor + ((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) ) * SymbolInfo.point * 0.8)           
                       print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V4 - M5")


                 sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
                 if sell_positions_with_open_prices:
                   for ticket, open_price in sell_positions_with_open_prices.items():
                     positions = MT5.positions_get()
                     for position_info in positions:
                      if position_info.symbol == self.Pair :
                         Botdashboard(54 , self.Pair)
                         return
                 tt = (floor - FrameRatesM5.iloc[-1]['open']) / (SymbolInfo.point)      
                 if Ca3_c < Ca3_o and Ca2_c < Ca2_o and Ca2_c < floor and tt < high_low_diff * 0.3 and Direction == "DOWN" : #Ca3_c < floor and
                   #if time.time() - PublicVarible.last_message_time >= 2 :
                       #PublicVarible.last_message_time = time.time() 
                       Text = f"🔻🔻 سیگنال فروش {self.Pair} 🔻🔻"
                       PromptToTelegram(Text)  
                       EntryPrice = SymbolInfo.ask                                                                                        ######### قیمت  ورود به معامله ##########
                       if self.Pair == 'XAUUSDb' : Volume = 0.01
                       else:  Volume = 0.03                                                    #########  محاسه حجم ورود به معامله ##########
                       SL = roof + (20 * SymbolInfo.point)                                                                               #########  تعیین حدضرر معامله #########
                       TP1 = roof - ((round(high_low_diff,2) - (abs(Basefloor - Baseroof) / (SymbolInfo.point)) ) * SymbolInfo.point * 0.8)    
                       print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                       OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V4 - M5")


             else:
                 print("Failed to retrieve values.")
                 return
             
"""                  
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
"""