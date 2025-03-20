import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
class SupplyDemandStrategyV7():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
       
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V7 M15 H & S ")
          # ارسال پیام
          
          Time_Signal = 1
          high_low_diff = 0 
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 250)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty: 
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)
         

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
            

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()

             CH2 = FrameRatesM15.iloc[-2]['high']
             CL2 = FrameRatesM15.iloc[-2]['low']
             CO2 = FrameRatesM15.iloc[-2]['open']
             CC2 = FrameRatesM15.iloc[-2]['close']

             CH3 = FrameRatesM15.iloc[-3]['high']
             CL3 = FrameRatesM15.iloc[-3]['low']
             CO3 = FrameRatesM15.iloc[-3]['open']
             CC3 = FrameRatesM15.iloc[-3]['close']

             CH4 = FrameRatesM15.iloc[-4]['high']
             CL4 = FrameRatesM15.iloc[-4]['low']
             CO4 = FrameRatesM15.iloc[-4]['open']
             CC4 = FrameRatesM15.iloc[-4]['close']
             current_time = time.time()

             if CH4 < CH3 and CH3 > CH2 and CC2 < CL3 and CC2 < CL4 : 
                 if current_time - PublicVarible.last_execution_timeM15 >= 900:  
                     PromptToTelegram(f"الگوی سرو شانه نزولی در تاریم فریم M15 {self.Pair}")
                     PublicVarible.last_execution_timeM15 =  time.time()

             elif CL4 > CL3 and CL3 > CL2  and CC2 > CH3 and CC2 > CH4 : 
                 if current_time - PublicVarible.last_execution_timeM15 >= 900:  
                     PromptToTelegram(f"الگوی سرو شانه صعودی در تاریم فریم M15 {self.Pair}")
                     PublicVarible.last_execution_timeM15 =  time.time()
            
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500