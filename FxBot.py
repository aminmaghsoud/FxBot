from decimal import ROUND_UP
from math import ceil
from pprint import pprint
import MetaTrader5 as MT5
import pandas as PD
import time
from pathlib import Path
from datetime import datetime, timedelta
import PublicVarible
from Utility import *
from SupplyDemandStrategyV5 import * # Prop Account
from SupplyDemandStrategyV7 import *
from SupplyDemandStrategyV8 import *
from SupplyDemandStrategyV9 import *
from SupplyDemandStrategyV1 import *
from SupplyDemandStrategyV2 import *
from SupplyDemandStrategyV3 import *
from SupplyDemandStrategyV4 import *
from Utility import *
import sys
import pytz
import requests
from colorama import init, Fore, Back, Style
import pandas_ta as PTA
import asyncio
import telegram
import psutil

########################################################################################################
class FxBot():
      def __init__(self):
          print("Start Robot Pirouz...")
          print("*************************************")
########################################################################################################
      def Main(self, BotId:int):
         
          GetConfiguration(BotId = BotId)
          Prompt("*************************************")

          GetTerminalInfo()
          Prompt("*************************************")

          if LoginAccount(Username= PublicVarible.Username, Password= PublicVarible.Password, Server= PublicVarible.Server, Timeout= PublicVarible.Timeout):
             Prompt("Connected to account {}".format(PublicVarible.Username))
          else:
             Prompt("Failed to connect {}, error code: {}".format(PublicVarible.Username, MT5.last_error()))
             Quit()
          Prompt("*************************************")

          UpdateLastRunTime()
          Prompt("*************************************")

          GetLastTelegramCommand()
          Prompt("*************************************")

          ##############################################Start Setting############################################
          Balance = GetBalance()
          if Balance >= 1000:
              A =  Balance // 1000
              Balance = round(A * 1000)

          PublicVarible.LossPrecent = -0.15   ##*********جدید*********
          PublicVarible.targetProfit = 0.06
          PublicVarible.TrailingTP = Balance * 2
          PublicVarible.TrailingSL = Balance * PublicVarible.LossPrecent
          PublicVarible.LastStoplossChange = None
          PublicVarible.lastclose = 0
          PublicVarible.Botstatus = 0
          PublicVarible.LastBuyPrice = 0
          PublicVarible.LastSellPrice = 0
          PublicVarible.MFIover = 1 
          PublicVarible.firstBuy = 100
          PublicVarible.firstSell = 100 
          PublicVarible.last_message_time = time.time()
          ########################################################################################################
          
          init()
          #init(autoreset=True)  # فعال کردن خودکار تنظیمات
          Style.NORMAL = ''
          # Print the text "PIRUZ" using the custom font
          print_custom_text("PIRUZ")
          print("\n")
          while True:
                # چک کردن زمان انقضاء ربات
                if (PublicVarible.ExpireAt - datetime.now()).total_seconds() < 0:
                   print("Bot has expired")
                   time.sleep(1)
                   continue
                
         ###################################################Supertrend_testM5#####################################################
                
                
                 
          ########################################################################################################


                if PublicVarible.StartBot == True: # ربات استارت بود روی مارکت کار کند
                   #   NewsTime = False
                   #   for Item in PublicVarible.News:
                   #       TimeBeforeNews = datetime.strptime(Item['DateTime'], "%Y-%m-%d %H:%M:%S") - timedelta(minutes = PublicVarible.StopTradesBeforeNews)
                   #       TimeAfterNews = datetime.strptime(Item['DateTime'], "%Y-%m-%d %H:%M:%S") + timedelta(minutes = PublicVarible.StopTradesAfterNews)
                   #       if (datetime.utcnow() >= TimeBeforeNews) and (datetime.utcnow() <= TimeAfterNews):
                   #          Prompt(f"{Item['Title']}... Trade is temporarily suspended")
                   #          NewsTime = True
                   #   
                   #   if NewsTime:
                   #      continue
                   #system( 'cls' )
                   
                   for Item in PublicVarible.Pair:
                       LastTick = MT5.symbol_info_tick(Item['Name'])
                       if Item['Tick'] != LastTick.time:
                          Item['Tick'] = LastTick.time
                          
                          


                          # بروزرسانی داده های مالی
                          SymbolInfo = MT5.symbol_info(Item['Name'])
                          print (Fore.BLACK,Back.LIGHTWHITE_EX,"Item Name                                               Result",Back.LIGHTBLUE_EX,"     Smart Pirouz is hunting ...    ", datetime.now().time(),Back.RESET,Fore.RESET,"\n" )
                          for index, pair_info in enumerate(PublicVarible.Pair):
                           if pair_info['Name'] == Item['Name']:
                               print(f" The index is: {index + 1}")
                               break 
                          #print (Fore.LIGHTWHITE_EX,Back.BLACK," Number of Added Pair: ", len(PublicVarible.Pair),Back.RESET)
                          print (Fore.BLACK,Back.LIGHTBLUE_EX ," Symbol  :  ", SymbolInfo.name,Back.RESET,Fore.RESET,"                                 Point : ","{:.10f}".format(SymbolInfo.point))
                          print ("            ",Back.RESET,Fore.RESET,"                                           spread: ",round(SymbolInfo.spread,1))
                          print ("            ",Back.RESET,Fore.RESET,"                                           TP pip: ",round(SymbolInfo.spread,1)*3/10 ,"\n" )
                          

                          if (datetime.now() - PublicVarible.LastDatetimeRobotIsReady).total_seconds() / 60 > 45:
                            PublicVarible.LastDatetimeRobotIsReady = datetime.now() 
                            Statistics()
                            PromptToTelegram(Text= "📌 Robot Pirouz is ready, market is open")

                          A = SupplyDemandStrategyV7(Pair = Item['Name'])
                          #B = SupplyDemandStrategyV8(Pair = Item['Name'])
                          #D = SupplyDemandStrategyV1(Pair = Item['Name']) #لگ سریع
                          E = SupplyDemandStrategyV2(Pair = Item['Name']) #Leg and trade 
                         # C = SupplyDemandStrategyV9(Pair = Item['Name']) 
                         # F = SupplyDemandStrategyV3(Pair = Item['Name']) #معاملات معکوس
                          G = SupplyDemandStrategyV4(Pair = Item['Name'])
                          PublicVarible.Executor.submit(A.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) #Posision Modify olny
                          #PublicVarible.Executor.submit(B.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) #XAUUSD M1
                          #PublicVarible.Executor.submit(D.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) #XAUUSD M5
                          PublicVarible.Executor.submit(E.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) #Leg and trade
                          #PublicVarible.Executor.submit(C.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) # other M5
                          #PublicVarible.Executor.submit(F.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) # other M15
                          #PublicVarible.Executor.submit(G.Main(), Item['Name'], TimeFrame= ConvertStringToTimeFrame(Item['TimeFrame'])) # XAUUSD M5 Spike


                          CloseAllPosition(Pair= Item['Name'])
                          

                       else:
                          SymbolInfo = MT5.symbol_info(Item['Name'])
                          print (Fore.BLUE,Back.LIGHTWHITE_EX,"Item Name                                               Result",Back.RED,Fore.LIGHTWHITE_EX," The market does not move ...    ", datetime.now().time(),Back.RESET,Fore.RESET,"\n" )
                          for index, pair_info in enumerate(PublicVarible.Pair):
                           if pair_info['Name'] == Item['Name']:
                               print(f" The index is: {index + 1}")
                               break
                          #text =colored(" Symbol : {SymbolInfo.name}" , 'red' , attrs=['reverse' , 'blink'])
                          print (Fore.LIGHTWHITE_EX,Back.RED ," Symbol  :  ", SymbolInfo.name,Back.RESET,Fore.RESET,"                                 Point : ","{:.10f}".format(SymbolInfo.point) )
                          print ("            ",Back.RESET,Fore.RESET,"                                           spread: ",round(SymbolInfo.spread,1))
                          print ("            ",Back.RESET,Fore.RESET,"                                           TP pip: ",round(SymbolInfo.spread,1)*3/10 ,"\n" )
                          
                          Botdashboard(2 , Item['Name'])
                          CloseAllPosition(Pair= Item['Name'])
                          

                ProcessTelegramCommand()
                time.sleep(1)
                
########################################################################################################
if __name__ == '__main__':
   PD.set_option('display.max_columns', 500)
   PD.set_option('display.width', 1700)
   if len(sys.argv) == 1:
      print("There is no argument bot Id")
      quit()
   elif len(sys.argv) == 2:
      print("There is no argument Mode")
      quit()

   BotId = int(sys.argv[1])
   Mode = sys.argv[2]
   if Mode == "Run":
      _FxBot = FxBot()
      _FxBot.Main(BotId)
   elif Mode == "Backtest":
        ClassName = sys.argv[3]
        vars()[ClassName]()