import pandas as PD
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import os

class GetData1():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          if self.Pair !='XAUUSDb' : return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ GetData1 M5 XAUUSDb ")
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
                   
                   # ذخیره اطلاعات در فایل
                   file_path = r"C:\CandleData\XAUUSDb_M5.csv"
                   os.makedirs(os.path.dirname(file_path), exist_ok=True)
                   
                   # ذخیره با فرمت CSV
                   FrameRatesM5.to_csv(file_path, sep='\t', encoding='utf-8')
                   print(f"Data saved to {file_path}")
                   
                   # نمایش اطلاعات ذخیره شده
                   print("\nLast 5 candles:")
                   print(FrameRatesM5.tail())

             