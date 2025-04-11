import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO
import math
import os

class LegAnalyzer():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
      data_dir = "C:\\Fxbot\\config"
      csv_file = None
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair

##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ LegAnalyzer  ")
          # ارسال پیام
          
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 20)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
           
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()

             trend_C = 0
             close_C = FrameRatesM5.iloc[-2]['close']
             high_C = FrameRatesM5.iloc[-2]['high'] 
             low_C = FrameRatesM5.iloc[-2]['low']
             high_C_O = FrameRatesM5.iloc[-3]['high'] 
             low_C_O = FrameRatesM5.iloc[-3]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             
#########################  بررسی قدرت کندل خروج    #########################    
             LowerLLA = PublicVarible.LowerLLA
             HigherHLA = PublicVarible.HigherHLA
             #print(f"Lower low = {PublicVarible.LowerLLA} \nhigher high = {PublicVarible.HigherHLA}")

             if  close_C >= One_third_UP and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down and close_C < low_C_O :
                 trend_C = -1
             elif close_C > One_third_Down and close_C < One_third_UP and close_C > high_C_O :
                 trend_C = +2
             elif close_C > One_third_Down and close_C < One_third_UP and  close_C < low_C_O :
                 trend_C = -2
    
             #### شناسایی لگ نزولی
             end_index = -16
             current_index = -3
             count = 1
             Text = None
             if high_C > (high_C_O ) :# and (FrameRatesM5.iloc[-2]['low'] > FrameRatesM5.iloc[-3]['low']) : 
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       
                       if Now_c_H < Old_c_H :# and Now_c_L < Old_c_L :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
            #### مقداردهی سقف و کف BOS
             if count > 2 : 
                legtype = "Bearish"
                PublicVarible.Leg_startLA = FrameRatesM5.iloc[current_index]['high']
                PublicVarible.high_low_diffLA  = round((abs( FrameRatesM5['low'].iloc[current_index : -1 ].min() - FrameRatesM5.iloc[current_index]['high'])) / (SymbolInfo.point),2)
                if round(round(abs(FrameRatesM5.iloc[-2]['high'] - FrameRatesM5['low'].iloc[current_index : -1 ].min()) / (SymbolInfo.point) / 10, 2) / PublicVarible.high_low_diffLA  * 1000,1) < 50 : 
                 leg_contorol = 150
                 if PublicVarible.high_low_diffLA  > (leg_contorol) and PublicVarible.high_low_diffLA  < (1200 ) : 
                  PublicVarible.HigherHLA = high_C 
                  PublicVarible.LowerLLA = low_C 
                  PublicVarible.BasefloorLA = FrameRatesM5['low'].iloc[current_index : -1 ].min() 
                  PublicVarible.BaseroofLA = FrameRatesM5.iloc[-2]['high']
                  PublicVarible.range_heightLA = round(abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)
                  
             ## شناسایی لگ صعودی
             end_index = -16
             current_index = -3
             count = 1
             Text = None       
             if (low_C < low_C_O - (SymbolInfo.point * 2)) :# and (FrameRatesM5.iloc[-2]['high'] < FrameRatesM5.iloc[-3]['high']) :
                   while current_index > end_index : 
                       Now_c_H = FrameRatesM5.iloc[current_index]['high']
                       Old_c_H = FrameRatesM5.iloc[current_index - 1]['high'] 
                       Now_c_L = FrameRatesM5.iloc[current_index]['low']
                       Old_c_L = FrameRatesM5.iloc[current_index - 1]['low']
                       if  Now_c_L > Old_c_L :# and Now_c_H > Old_c_H :
                          count += 1 
                          current_index -= 1
                       else : 
                           break
            ## مقداردهی سقف و کف BOS
             if count > 2 : 
              legtype = "Bullish"           
              PublicVarible.Leg_startLA = FrameRatesM5.iloc[current_index]['low']
              PublicVarible.high_low_diffLA  = round((abs(FrameRatesM5.iloc[current_index : -1]['high'].max() - FrameRatesM5.iloc[current_index]['low'])) / (SymbolInfo.point) , 2)
              if  round((round(abs((FrameRatesM5.iloc[current_index : -1]['high'].max()) - ( FrameRatesM5.iloc[-2]['low'])) / (SymbolInfo.point) / 10, 2)) / PublicVarible.high_low_diffLA * 1000,1) < 50 :
                 leg_contorol = 150
                 if PublicVarible.high_low_diffLA  > (leg_contorol) and PublicVarible.high_low_diffLA  < (1200 ) : 
                  PublicVarible.HigherHLA = high_C 
                  PublicVarible.LowerLLA = low_C  
                  PublicVarible.BaseroofLA = FrameRatesM5.iloc[current_index : -1]['high'].max()
                  PublicVarible.BasefloorLA = FrameRatesM5.iloc[-2]['low']
                  PublicVarible.range_heightLA = round(abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) / (SymbolInfo.point) / 10, 2)

########################  پیداکردن بالاترین سقف و پایین ترین کف رنج   ################################

             if PublicVarible.BaseroofLA != 0 and close_C < PublicVarible.BaseroofLA and close_C > PublicVarible.BasefloorLA : 
               if high_C > PublicVarible.HigherHLA : 
                  PublicVarible.HigherHLA = high_C 
               if low_C < PublicVarible.LowerLLA: 
                  PublicVarible.LowerLLA = low_C
             elif PublicVarible.BasefloorLA == 0 : 
                  PublicVarible.LowerLLA = PublicVarible.HigherHLA  = 0

################################### بررسی الگوی سر و شانه #####################################

             CH2 = FrameRatesM5.iloc[-2]['high']
             CL2 = FrameRatesM5.iloc[-2]['low']
             CC2 = FrameRatesM5.iloc[-2]['close']

             CH3 = FrameRatesM5.iloc[-3]['high']
             CL3 = FrameRatesM5.iloc[-3]['low']
             CC3 = FrameRatesM5.iloc[-3]['close']

             CH4 = FrameRatesM5.iloc[-4]['high']
             CL4 = FrameRatesM5.iloc[-4]['low']

             CH5 = FrameRatesM5.iloc[-5]['high']
             CL5 = FrameRatesM5.iloc[-5]['low']

             if PublicVarible.BasefloorLA == 0 : PublicVarible.HS_UpLA = PublicVarible.HS_DownLA = 0 
             elif PublicVarible.BasefloorLA != 0 and PublicVarible.HS_UpLA == 0 and PublicVarible.HS_DownLA == 0 : 
               if (CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4) or ((CC3 >= CL4 or CC3 >= CL5 ) and (CH5 < CH4 and CH4 > CH3 and CC2 < CL4 and CC2 < CL5 and CC2 < CL3)): 
                     PublicVarible.HS_DownLA = 1
               elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 or ((CC3 <= CH4 or CC3 <= CH5 ) and (CL5 > CH4 and CL4 < CL3 and CC2 > CH4 and CC2 > CH5 and CC2 > CH3)):
                     PublicVarible.HS_UpLA = 1 

#Buy####################  بررسی شرط خروج قیمت از سقف و انجام معامله خرید ######################
             
             if close_C > PublicVarible.BaseroofLA and close_C < (PublicVarible.BaseroofLA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofLA != 0 :
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                Text = f" مقدار و قدرت خروج قیمت از سقف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C >= (PublicVarible.BaseroofLA + (SymbolInfo.point * 5)) and PublicVarible.BaseroofLA != 0 and close_C > HigherHLA : 
                print(f"price is {close_C} and Upper Roof {PublicVarible.BaseroofLA} ")
                if  True :   
                   if trend_C == +1 : 
                       Text += f"خروج قیمت از #سقف با قدرت #زیاد توسط خریداران  🐮 \n "
                   elif trend_C == +2 : 
                       PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   if trend_C == -1 or trend_C == -2 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
#Buy                  
                if  trend_C == +1  : 
                   if  (abs(close_C - PublicVarible.BaseroofLA) < (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA) * 0.75 )):       
                       Buytrade = "Buy" 
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0  


#Sell ####################  بررسی شرط خروج قیمت از کف و انجام معامله فروش ######################

             if close_C < PublicVarible.BasefloorLA and close_C > (PublicVarible.BasefloorLA + (SymbolInfo.point * 5)) and PublicVarible.BasefloorLA != 0 :
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                Text = f" مقدار و قدرت خروج قیمت از کف #نامناسب است \n ⚠️پاک کردن  مقادیر سقف و کف ⚠️"
                #results = send_telegram_messages(Text, PublicVarible.chat_ids)

             elif close_C <= (PublicVarible.BasefloorLA - (SymbolInfo.point * 5)) and PublicVarible.BasefloorLA != 0 and close_C < LowerLLA : 
                print(f"price is {close_C} and Under floor {PublicVarible.BasefloorLA} ")
                if True :   
                   if trend_C == -1 : 
                       Text += f"خروج قیمت از #کف با قدرت #زیاد توسط فروشندگان 🐻 \n"
                   elif trend_C == -2 :
                        PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 0 :
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
                   elif trend_C == 1 or trend_C ==2:
                      PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
#Sell
                
                if  (trend_C == -1 ) :
                   if  (abs(close_C - PublicVarible.BasefloorLA) < (abs(PublicVarible.BaseroofLA - PublicVarible.BasefloorLA)* 0.75) ) :
                     Selltrade = "Sell" 
                PublicVarible.BaseroofLA = PublicVarible.BasefloorLA = 0
      
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500

