﻿import math
from pickle import TRUE
import MetaTrader5 as MT5
from datetime import datetime, timedelta
import pandas as PD
import pandas_ta as PTA
import mplfinance as MPF
import uuid
import PublicVarible
import pyodbc
import warnings
import requests
from colorama import Fore, init , Back
import os
import telegram
from art import *
import jdatetime
import requests
import time
import MetaTrader5 as MT5
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO
import pandas as pd
import pandas_ta as pta
from GoldPricePredictor import *
from GoldPricePredictorLSTM import * 
from GoldPricePredictorM5 import *
from GoldPricePredictorM5_XGB import GoldPricePredictorM5_XGB
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import random

warnings.filterwarnings('ignore')

# صف برای ذخیره پیام‌های جدید
message_queue = queue.Queue()

# تابع برای نمایش پنجره
def show_text_window():
    def update_text():
        try:
            while True:
                # دریافت پیام جدید از صف
                message = message_queue.get_nowait()
                # اضافه کردن پیام به پنجره
                text_widget.insert(tk.END, message + "\n")
                text_widget.see(tk.END)  # اسکرول به آخرین پیام
                message_queue.task_done()
        except queue.Empty:
            pass
        # برنامه‌ریزی برای اجرای مجدد بعد از 100 میلی‌ثانیه
        root.after(100, update_text)

    # ایجاد پنجره اصلی
    root = tk.Tk()
    root.title("Bot Messages")
    root.geometry("800x600")

    # ایجاد ویجت برای نمایش متن
    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30)
    text_widget.pack(expand=True, fill='both', padx=10, pady=10)

    # شروع به‌روزرسانی خودکار متن
    update_text()

    # اجرای پنجره
    root.mainloop()

# تابع برای شروع پنجره در یک ترد جداگانه
def start_text_window():
    window_thread = threading.Thread(target=show_text_window, daemon=True)
    window_thread.start()

# تابع برای ارسال پیام به پنجره
def send_to_window(message: str):
    message_queue.put(message)

########################################################################################################
def Prompt(Text: str):
    String = f"Bot{PublicVarible.Id} " + datetime.now(PublicVarible.BrokerTimeZone).strftime("%Y-%m-%d %H:%M:%S") + " => " + Text
    print(String)
    PublicVarible.LstLog.append(String)
    send_to_window(String)  # ارسال پیام به پنجره ویندوزی
    
    if len(PublicVarible.LstLog) % 100 == 0:
        with open('Log.Txt', 'a', encoding='utf-8') as LogTxt:
            for Item in PublicVarible.LstLog:
                LogTxt.write(f"{Item}\n")
        PublicVarible.LstLog.clear()

########################################################################################################
def PromptToTelegram(Text:str):
    ApiURL = f'https://api.telegram.org/bot{PublicVarible.TelegramToken}/sendMessage'
    for Item in PublicVarible.TelegramChatId:
        try:
            requests.post(ApiURL, json={'chat_id': Item, 'text': Text})
        except Exception as e:
            print(e)
########################################################################################################
def ExportToCSV(Pair:str, TimeFrame:str, Period:int, FileName:str):
    Rates = MT5.copy_rates_from_pos(Pair, ConvertStringToTimeFrame(TimeFrame), 0, Period)
    if Rates is not None:
       FrameRates = PD.DataFrame(Rates)
       if not FrameRates.empty:
          FrameRates['DateTime'] = PD.to_datetime(FrameRates['time'], unit='s')
          FrameRates = FrameRates.set_index('DateTime')
          FrameRates = FrameRates.drop('time', axis=1)
          FrameRates = FrameRates.drop('tick_volume', axis=1)
          FrameRates = FrameRates.drop('spread', axis=1)
          FrameRates = FrameRates.drop('real_volume', axis=1)
          FrameRates.rename(columns = {'open':'Open'}, inplace = True)
          FrameRates.rename(columns = {'high':'High'}, inplace = True)
          FrameRates.rename(columns = {'low':'Low'}, inplace = True)
          FrameRates.rename(columns = {'close':'Close'}, inplace = True)
          FrameRates.to_csv(fr'Data\{FileName}.csv', sep='\t', encoding='utf-8')
          #FrameRates.to_csv(f'Data\\{FileName}.csv', sep='\t', encoding='utf-8')

########################################################################################################
def LoadFromCSV(FileName:str, DateTimeColumnName:str):
    Rates = PD.read_csv(fr'Data\{FileName}.csv', sep='\t', encoding='utf-8')
    if Rates is not None:
       FrameRates = PD.DataFrame(Rates)
       FrameRates[DateTimeColumnName] = PD.to_datetime(FrameRates[DateTimeColumnName])
       FrameRates = FrameRates.set_index(DateTimeColumnName)
       return FrameRates
    else:
       return None
########################################################################################################
def GetConfiguration(BotId:int):
    Text = "🔸Hello, dear" + "\n" + "من پیروز هستم... یوزپلنگ ایرانی! 🐆 یک ربات معامله‌گر هوشمند و متخصص در بازار فارکس. همان‌طور که می‌دانید، بازارهای مالی پرریسک هستند، اما من با تکیه بر توانایی‌های خلاقانه‌ام در شناسایی سریع روندها، مدیریت سرمایه و کنترل معاملات، آماده‌ام تا بیشترین سود را کسب کرده و از ضررها جلوگیری کنم. 🚀" + "\n"
    if not MT5.initialize():
       Prompt("Initialize() Failed, Error Code = {}".format(MT5.last_error()))
       PromptToTelegram(Text= "Initialize() Failed, Error Code = {}".format(MT5.last_error()))
       Quit()

    AccountInfo = MT5.account_info()
    if AccountInfo is None:
       Prompt("Account info is None")
       PromptToTelegram(Text= "Account info is None")
       Quit()

    Conn = pyodbc.connect(PublicVarible.ConnectionString)
    Cmd = PD.read_sql_query(f"SELECT TOP(1) * FROM Bot WHERE Id = {BotId}", Conn)
    Bot = PD.DataFrame(Cmd)
    if Bot.empty:
       Prompt("There is no bot")
       PromptToTelegram(Text= "There is no bot")
       Quit()

    Prompt("Current bot config")
    Text += "\n" + "⚙️ Current bot config"

    PublicVarible.Id = Bot.iloc[0]['Id']
    Prompt(f"Bot id is {PublicVarible.Id}")
    Text += "\n" + f"🛑 Id: {PublicVarible.Id}"

    Cmd = PD.read_sql_query(f"SELECT TOP(1) Username, Password, Server, Timeout FROM Account WHERE BotId = {PublicVarible.Id} AND IsActive = 1", Conn)
    Account = PD.DataFrame(Cmd)
    if Account.empty:
          Prompt("There is no active account")
          PromptToTelegram(Text= "There is no active account")
          Quit()

    PublicVarible.Username = Account.iloc[0]['Username']
    PublicVarible.Password = Account.iloc[0]['Password']
    PublicVarible.Server = Account.iloc[0]['Server']
    PublicVarible.Timeout = Account.iloc[0]['Timeout']
    Prompt("Login :" + PublicVarible.Username)
    Text += "\n" + "🙍‍♂️ Login :" + PublicVarible.Username
    Prompt("Password :" + PublicVarible.Password)
    Text += "\n" + "🔑 Password :" + PublicVarible.Password
    Prompt("Server :" + PublicVarible.Server)
    Text += "\n" + "💻 Server :" + PublicVarible.Server
    Prompt("Timeout :" + str(PublicVarible.Timeout))
    Text += "\n" + "⏱️ Timeout :" + str(PublicVarible.Timeout)

    PublicVarible.Name = Bot.iloc[0]['Name']
    Prompt("Name :" + str(PublicVarible.Name))
    Text += "\n" + "🏷️ Name :" + str(PublicVarible.Name)

    PublicVarible.MaxOpenTrades = Bot.iloc[0]['MaxOpenTrades']
    Prompt("Max open trades :" + str(PublicVarible.MaxOpenTrades))
    Text += "\n" + "✅ Max open trades :" + str(PublicVarible.MaxOpenTrades)

    PublicVarible.StakeCurrency = Bot.iloc[0]['StakeCurrency']
    Prompt("Stake currency :" + str(PublicVarible.StakeCurrency))
    Text += "\n" + "💵 Stake currency :" + str(PublicVarible.StakeCurrency)

    Prompt(f"Balance :{str(GetBalance())}$")
    Text += "\n" + f"💰 Balance :{str(GetBalance())}$"

    PublicVarible.VirtualBalance = Bot.iloc[0]['VirtualBalance']
    Prompt(f"Virtual balance :{str(PublicVarible.VirtualBalance)}$")
    Text += "\n" + f"💰 Virtual balance :{str(PublicVarible.VirtualBalance)}$"

    Prompt(f"Equity :{str(GetEquity())}$")
    Text += "\n" + f"💰 Equity :{str(GetEquity())}$"

    PublicVarible.LotIncreaseRatio = Bot.iloc[0]['LotIncreaseRatio']
    Prompt(f"Lot increase ratio :{str(PublicVarible.LotIncreaseRatio)}$")
    Text += "\n" + f"💰 Lot increase ratio :{str(PublicVarible.LotIncreaseRatio)}$"

    Prompt(f"Lot :{GetLotSize()}")
    Text += "\n" + f"♦️ Lot :{GetLotSize()}"

    PublicVarible.Leverage = AccountInfo.leverage
    Prompt(f"Leverage :{str(PublicVarible.Leverage)}")
    Text += "\n" + f"♦️ Leverage :{str(PublicVarible.Leverage)}"

    PublicVarible.CreateAt = Bot.iloc[0]['CreateAt']
    Prompt(f"Create date :{PublicVarible.CreateAt.strftime('%Y-%m-%d')}")
    Text += "\n" + f"⏰ Create date :{PublicVarible.CreateAt.strftime('%Y-%m-%d')}"

    PublicVarible.ExpireAt = Bot.iloc[0]['ExpireAt']
    Prompt(f"Expire date :{PublicVarible.ExpireAt.strftime('%Y-%m-%d')}")
    Text += "\n" + f"⏰ Expire date :{PublicVarible.ExpireAt.strftime('%Y-%m-%d')}"
    if (PublicVarible.ExpireAt - datetime.now()).total_seconds() < 0:
       Text += "\n" + f"⛔ Bot has expired ⛔"

    Text += "\n" + "Currency pairs :"
    Cmd = PD.read_sql_query(f"SELECT Name, TimeFrame FROM Pair WHERE BotId = {PublicVarible.Id}", Conn)
    Pair = PD.DataFrame(Cmd)
    if not Pair.empty:
          for Index, Item in Pair.iterrows():
              SymbolInfo = MT5.symbol_info(Item['Name'])
              if SymbolInfo is None:
                 Prompt("Symbol {} is None".format(Item['Name']))
                 Quit()
              LastTick = MT5.symbol_info_tick(Item['Name'])
              if LastTick is not None:
                if LastTick.time is not None : 
                    PublicVarible.Pair.append({"Name": Item['Name'], "TimeFrame": Item['TimeFrame'], "Tick": LastTick.time})
                    Text += "\n" + f"▫️ {Item['Name']}"                
    
    if len(PublicVarible.Pair) == 0:
          Prompt("No currency pairs have been registered")
          Quit()

    Prompt("Currency pairs :" + str(PublicVarible.Pair))
    Prompt(str(len(PublicVarible.Pair)) + " pairs added")

    PublicVarible.TelegramToken = Bot.iloc[0]['TelegramToken']
    #PublicVarible.TelegramChatId = Bot.iloc[0]['TelegramChatId']

    PromptToTelegram(Text= Text)
########################################################################################################

def GetConfiguration1(BotId:int): #خواندان از فایل txt
    file_path = r"C:\Fxbot\Config\Config.pruz"

    if not os.path.exists(file_path):
        Prompt("Config file not found!")
        PromptToTelegram(Text="Config file not found!")
        Quit()

    # خواندن اطلاعات از فایل
    config = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    Text = "🔸Hello, dear\n" + "من پیروز هستم... یوزپلنگ ایرانی! 🐆 یک ربات معامله‌گر هوشمند و متخصص در بازار فارکس.\n"

    # مقداردهی اطلاعات ربات
    PublicVarible.Id = int(config.get("Id", 2))
    PublicVarible.Name = config.get("pairName", "")
    PublicVarible.MaxOpenTrades = int(config.get("MaxOpenTrades", 0))
    PublicVarible.StakeCurrency = config.get("StakeCurrency", "USD")
    PublicVarible.VirtualBalance = float(config.get("VirtualBalance", 0))
    PublicVarible.LotIncreaseRatio = float(config.get("LotIncreaseRatio", 1.0))
    PublicVarible.CreateAt = datetime.strptime(config.get("CreateAt", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
    PublicVarible.ExpireAt = datetime.strptime(config.get("ExpireAt", "2100-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
    PublicVarible.TelegramToken = config.get("TelegramToken", "")

    # مقداردهی اطلاعات حساب
    PublicVarible.Username = config.get("Username", "")
    PublicVarible.Password = config.get("Password", "")
    PublicVarible.Server = config.get("Server", "")
    PublicVarible.Timeout = int(config.get("Timeout", 30))

    # بررسی و مقداردهی متاتریدر
    if not MT5.initialize():
        Prompt("Initialize() Failed, Error Code = {}".format(MT5.last_error()))
        PromptToTelegram(Text="Initialize() Failed, Error Code = {}".format(MT5.last_error()))
        Quit()

    AccountInfo = MT5.account_info()
    if AccountInfo is None:
        Prompt("Account info is None")
        PromptToTelegram(Text="Account info is None")
        Quit()

    PublicVarible.Leverage = AccountInfo.leverage

    # مقداردهی لیست جفت‌ارزها
    PublicVarible.Pair = []
    currency_pairs = config.get("CurrencyPairs", "").split(",")
    for pair in currency_pairs:
        pair = pair.strip()
        if pair:
            SymbolInfo = MT5.symbol_info(pair)
            if SymbolInfo is None:
                Prompt(f"Symbol {pair} is None")
                Quit()
            LastTick = MT5.symbol_info_tick(pair)
            if LastTick is not None and LastTick.time is not None:
                PublicVarible.Pair.append({"Name": pair, "TimeFrame": "M5", "Tick": LastTick.time})

    if len(PublicVarible.Pair) == 0:
        Prompt("No currency pairs have been registered")
        Quit()

    # نمایش اطلاعات
    Prompt(f"Bot id is {PublicVarible.Id}")
    Prompt(f"Name: {PublicVarible.Name}")
    Prompt(f"Username: {PublicVarible.Username}")
    Prompt(f"Server: {PublicVarible.Server}")
    Prompt(f"Leverage: {PublicVarible.Leverage}")
    Prompt(f"Pairs: {PublicVarible.Pair}")

    # ارسال پیام به تلگرام
    Text += f"\n🛑 Id: {PublicVarible.Id}"
    Text += f"\n🏷️ Name: {PublicVarible.Name}"
    Text += f"\n🙍‍♂️ Login: {PublicVarible.Username}"
    Text += f"\n🔑 Password: {PublicVarible.Password}"
    Text += f"\n💻 Server: {PublicVarible.Server}"
    Text += f"\n⏱️ Timeout: {PublicVarible.Timeout}"
    Text += f"\n✅ Max open trades: {PublicVarible.MaxOpenTrades}"
    Text += f"\n💵 Stake currency: {PublicVarible.StakeCurrency}"
    Text += f"\n💰 Virtual balance: {PublicVarible.VirtualBalance}$"
    Text += f"\n💰 Lot increase ratio: {PublicVarible.LotIncreaseRatio}$"
    Text += f"\n♦️ Leverage: {PublicVarible.Leverage}"
    Text += f"\n⏰ Create date: {PublicVarible.CreateAt.strftime('%Y-%m-%d')}"
    Text += f"\n⏰ Expire date: {PublicVarible.ExpireAt.strftime('%Y-%m-%d')}"
    
    if (PublicVarible.ExpireAt - datetime.now()).total_seconds() < 0:
        Text += "\n⛔ Bot has expired ⛔"

    Text += "\nCurrency pairs:"
    for pair in PublicVarible.Pair:
        Text += f"\n▫️ {pair['Name']}"

    PromptToTelegram(Text=Text)


########################################################################################################

def DailyReport():
    text = ""
    sum_deals_count = 0
    sum_profit = 0
    for days_ago in range(0, -7, -1):
        profit = 0
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        
        from_time = datetime(year, month, day, 0, 0, 0) + timedelta(days=days_ago)
        to_time = datetime(year, month, day, 23, 59, 59) + timedelta(days=days_ago)
        print(f"From {from_time} To {to_time}")
        history_orders = MT5.history_deals_get(from_time, to_time)
        
        if history_orders is None:
            Prompt(f"{from_time.strftime('%Y-%m-%d')} (0)  0$")
            text += "\n" + f"{from_time.strftime('%Y-%m-%d')} (0)  0$"
        elif len(history_orders) > 0:
            DF = PD.DataFrame(list(history_orders), columns=history_orders[0]._asdict().keys())
            print(DF)
            profit = DF['profit'].sum() + DF['swap'].sum() + DF['commission'].sum()
            sum_profit += profit
            sum_deals_count += len(DF.query('entry == 0'))
            Prompt(f"{from_time.strftime('%Y-%m-%d')} ({len(DF.query('entry == 0'))})  {round(profit, 2)}$")
            
            if profit > 0:
                text += "\n" + f"🟩 {from_time.strftime('%Y-%m-%d')} ({len(DF.query('entry == 0'))})  {round(profit, 2)}$"
            elif profit == 0:
                text += "\n" + f"🟨 {from_time.strftime('%Y-%m-%d')} ({len(DF.query('entry == 0'))})  {round(profit, 2)}$"
            else:
                text += "\n" + f"🟥 {from_time.strftime('%Y-%m-%d')} ({len(DF.query('entry == 0'))})  {round(profit, 2)}$"

    text += "\n" + "--------------------------" + "\n" + f"Sum ({sum_deals_count}) {round(sum_profit, 2)}$"
    PromptToTelegram(Text= text)
########################################################################################################
    
def ProfitByDay(Date:datetime):
    Profit = 0
    Year = Date.year
    Month = Date.month
    Day = Date.day
    
    From = datetime(Year, Month, Day, 0, 0, 0)
    To = datetime(Year, Month, Day, 23, 59, 59)
    
    HistoryOrders= MT5.history_deals_get(From, To)
    if HistoryOrders == None:
       return Profit
    elif len(HistoryOrders) > 0:
       DF = PD.DataFrame(list(HistoryOrders), columns= HistoryOrders[0]._asdict().keys())
       Profit = DF['profit'].sum()
     
    return Profit  
########################################################################################################
def CloseAllPosition(Pair:str):
     
    Profit = 0
    Positions = MT5.positions_get(symbol= Pair)
    
    if Positions is None:
       return
    elif len(Positions) > 0:
         Botdashboard(3 , Pair)
         Pos = PD.DataFrame(list(Positions), columns= Positions[0]._asdict().keys())
         Profit = Pos['profit'].sum() #+ Pos['swap'].sum() + Pos['commission'].sum()
         print ()
         Balance = GetBalance()
         if Profit > 0  : 
            print(Fore.LIGHTYELLOW_EX,"Total profit at this moment       ",Fore.LIGHTGREEN_EX,"                    ",round(Profit,2),Fore.RESET,"\n")
         else : 
            print(Fore.LIGHTYELLOW_EX,"Total profit at this moment       ",Fore.LIGHTRED_EX,"                   ",round(Profit,2),Fore.RESET,"\n")
        
         if Profit > Balance * 0.10 : 
            #MT5.Close(symbol= Pair)
            Prompt(f"Profit is {round(Profit, 2)}$ and Posision successfully closed by Smart StopLoss , Balance: {str(GetBalance())}$")
            PromptToTelegram(Text= f"❎ Profit is {round(Profit, 2)}$ (5%) Posision successfully closed by Smart StopLoss " + "\n" + f"💰 Balance: {str(GetBalance())}$")
         #  
         ##محاسبه حد سود متحرک
         #if Profit <= (Balance * -0.3) and PublicVarible.TrailingTP >= 0: 
         #          PublicVarible.TrailingTP = 0
         ##elif Profit < (Balance * -0.03) and PublicVarible.TrailingTP >= (Balance * -0.01): 
         #     #    PublicVarible.TrailingTP = (Balance * -0.01)
         #
         #if Profit <= PublicVarible.TrailingSL :
         #   #MT5.Close(symbol= Pair)
         #   Prompt(f"Profit is {round(Profit, 2)}$ and orders successfully closed by Trailing StopLoss and Stopped opening a new order !!! , Balance: {str(GetBalance())}$")
         #   PromptToTelegram(Text= f"❎ Profit is {round(Profit, 2)}$ and orders successfully closed by Trailing StopLoss and Stopped opening a new order !!! " + "\n" + f"💰 Balance: {str(GetBalance())}$")
         #   PublicVarible.TrailingSL =  (Balance * PublicVarible.LossPrecent) 
         #   PublicVarible.TrailingTP = Balance * 2
         #   #PublicVarible.CanOpenOrder = False
         #elif   Profit >= PublicVarible.TrailingTP :
         #   #MT5.Close(symbol= Pair)
         #   Prompt(f"Profit is {round(Profit, 2)}$ and orders successfully closed by Trailing Stoploss ! , Balance: {str(GetBalance())}$")
         #   PromptToTelegram(Text= f"❎ Profit is {round(Profit, 2)}$ and orders successfully closed by Trailing TakeProfit !" + "\n" + f"💰 Balance: {str(GetBalance())}$")
         #   PublicVarible.TrailingSL =  (Balance * PublicVarible.LossPrecent) 
         #   PublicVarible.TrailingTP = Balance * 2
         #
    return 1 
########################################################################################################
def Statistics():
    Text = ""
    Prompt("Max open trades: " + str(PublicVarible.MaxOpenTrades))
    Text += "\n" + "✅ Max open trades: " + str(PublicVarible.MaxOpenTrades)

    Prompt("Stake currency: " + str(PublicVarible.StakeCurrency))
    Text += "\n" + "💵 Stake currency: " + str(PublicVarible.StakeCurrency)

    Prompt(f"Balance: {str(GetBalance())}$")
    Text += "\n" + f"💰 Balance: {str(GetBalance())}$"

    Prompt(f"Equity: {str(GetEquity())}$")
    Text += "\n" + f"💰 Equity: {str(GetEquity())}$"

    Prompt(f"------------------------------------")
    Text += "\n" + f"------------------------------------"

    A = AnalyzePositions()
    Prompt(f"Profit: {str(round(A[0], 2))}$")
    Text += "\n" + f"💰 Profit: {str(round(A[0], 2))}$"

    Prompt(f"Total profit buy: {str(round(A[1], 2))}$")
    Text += "\n" + f"💰 Total profit buy: {str(round(A[1], 2))}$"

    Prompt(f"Total profit sell: {str(round(A[2], 2))}$")
    Text += "\n" + f"💰 Total profit sell: {str(round(A[2], 2))}$"

    Prompt(f"------------------------------------")
    Text += "\n" + f"------------------------------------"

    Prompt(f"Number of buy: {str(A[3])}")
    Text += "\n" + f"➕ Number of buy: {str(A[3])}"

    Prompt(f"Number of sell: {str(A[4])}")
    Text += "\n" + f"➖ Number of sell: {str(A[4])}"

    Prompt(f"------------------------------------")
    Text += "\n" + f"------------------------------------"

    Prompt(f"Volume: {str(round(A[5], 2))}")
    Text += "\n" + f"▫️ Volume: {str(round(A[5], 2))}"

    Prompt(f"Total buy volume: {str(round(A[6], 2))}")
    Text += "\n" + f"⬆️ Total buy volume: {str(round(A[6], 2))}"

    Prompt(f"Total sell volume: {str(round(A[7], 2))}")
    Text += "\n" + f"⬇️ Total sell volume: {str(round(A[7], 2))}"

    Prompt(f"------------------------------------")
    Text += "\n" + f"------------------------------------"

    #Prompt(f"Trailing stoploss: {str(round(PublicVarible.TrailingSL, 2))}$")
    #Text += "\n" + f"💰 Trailing stoploss: {str(round(PublicVarible.TrailingSL, 2))}$"

    #Prompt(f"Trailing TakeProfit: {str(round(PublicVarible.TrailingTP, 2))}$")
    #Text += "\n" + f"💰 Trailing takeprofit: {str(round(PublicVarible.TrailingTP, 2))}$"

    if PublicVarible.CanOpenOrder == True:
       Prompt(f"Can open new order: Yes")
       Text += "\n" + f"✔️ Can open new order: Yes"
    else:
       Prompt(f"Can open new order: No")
       Text += "\n" + f"❌ Can open new order: No"
    if PublicVarible.risk == 3 : 
             Prompt(f"Risk : High")
             Text += "\n" + f" ⚠️ Tradeing Risk >> High 🔴 "
    elif PublicVarible.risk == 2 : 
             Prompt(f"Risk: Medium")
             Text += "\n" + f" ⚠️ Tradeing Risk >> Medium 🟡"
    elif PublicVarible.risk == 1 : 
             Prompt(f"Risk: Low")
             Text += "\n" + f" ⚠️ Tradeing Risk >> Low 🟢"
    if PublicVarible.Quick_trade == False : 
             Text += "\n" + f" ⚠️ xauusd trade is OFF 🟢 "
    elif PublicVarible.Quick_trade == True : 
             Text += "\n" + f" ⚠️ xauusd trade is ON 🔴 "
    PromptToTelegram(Text= Text)

########################################################################################################
def ForceCloseAllPosition():
    for Item in PublicVarible.Pair:
        MT5.Close(symbol= Item['Name'])

    Prompt(f"Orders successfully closed and Stopped opening a new order, Balance: {str(GetBalance())}$")
    PromptToTelegram(Text= f"❎ Orders successfully closed and Stopped opening a new order" + "\n" + f"💰 Balance: {str(GetBalance())}$")
    PublicVarible.TrailingSL = -1 * GetBalance() * 0.10
    PublicVarible.LastStoplossChange = None
    #PublicVarible.CanOpenOrder = False
########################################################################################################
def GetLastTelegramCommand():
    Url = f"https://api.telegram.org/bot{PublicVarible.TelegramToken}/getUpdates?offset=-1"
    try:
        Data = requests.get(Url, timeout= 5).json()
        if Data['ok'] == True and len(Data['result']) > 0:
           PublicVarible.LastTelegramUpdateId = Data['result'][0]['update_id']
           Prompt(f"Last telegram update id {PublicVarible.LastTelegramUpdateId}")
    except Exception as e:
            print(e)
    
    return
########################################################################################################
def ProcessTelegramCommand():
    Url = ""
    if PublicVarible.LastTelegramUpdateId == -1:
       Url = f"https://api.telegram.org/bot{PublicVarible.TelegramToken}/getUpdates?offset=-1"
    else:
       Url = f"https://api.telegram.org/bot{PublicVarible.TelegramToken}/getUpdates?offset={PublicVarible.LastTelegramUpdateId + 1}"
    
    try:
        Data = requests.get(Url, timeout= 5).json()
        Command = ""
        if Data['ok'] == True and len(Data['result']) > 0:
           UpdateId = Data['result'][0]['update_id']
           if UpdateId > PublicVarible.LastTelegramUpdateId:
              PublicVarible.LastTelegramUpdateId = UpdateId
              Command = Data['result'][0]['message']['text']

        if Command == "/off_new_order":
           PublicVarible.CanOpenOrder = False
           Prompt("Stopped opening a new order")
           Text = f"⏹️ Stopped opening a new order"
           PromptToTelegram(Text= Text)
        elif Command == "/on_new_order":
           PublicVarible.CanOpenOrder = True
           Prompt("Started opening a new order")
           Text = f"▶️ Started opening a new order"
           PromptToTelegram(Text= Text)
        elif Command == "/close_all_position":
           ForceCloseAllPosition()
        elif Command == "/statistics":
           Statistics()
        elif Command == "/daily":
           DailyReport()
        elif Command == "/balance":
           Text = ""
           Prompt(f"Balance: {str(GetBalance())}$")
           Text += "\n" + f"💰 Balance: {str(GetBalance())}$"
           Prompt(f"Equity: {str(GetEquity())}$")
           Text += "\n" + f"💰 Equity: {str(GetEquity())}$"
           Prompt(f"Leverage: {str(PublicVarible.Leverage)}")
           Text += "\n" + f"♦️ Leverage: {str(PublicVarible.Leverage)}"
           PromptToTelegram(Text= Text)
        elif Command == "/license":
           Text = ""
           Offset = (PublicVarible.ExpireAt - datetime.now()).total_seconds()
           if Offset < 0:
              Text += "⛔ Bot has expired ⛔"
           elif Offset > 0:
              Text += f"{round(Offset / 86400)} days left"
           PromptToTelegram(Text= Text)
        elif Command == "/reboot_server":
              os.system('shutdown -t 0 -r -f')
        elif Command == "/risk_high":
             PublicVarible.risk= 3
             Text = ""
             Prompt(f"Risk is High Now !!!")
             Text += "♦️ Risk is #High Now !!!"
             PromptToTelegram(Text= Text)
        elif Command == "/risk_med":
             PublicVarible.risk= 2
             Text = ""
             Prompt(f"Risk is Medium Now !!!")
             Text += "♦️ Risk is #Medium Now !!!"
             PromptToTelegram(Text= Text)
        elif Command == "/risk_low":
             PublicVarible.risk= 1
             Text = ""
             Prompt(f"Risk is low Now !!!")
             Text += "♦️ Risk is #low Now !!!"
             PromptToTelegram(Text= Text)  
        elif Command == "/kissme":
             PromptToTelegram('بفرما ...')
             PromptToTelegram('😘')
             PromptToTelegram('😘')
             PromptToTelegram('😘')
        elif Command == "/quick_trade_off" :
             PublicVarible.Quick_trade = False
             PromptToTelegram("xauusd trade is OFF") 
        elif Command == "/quick_trade_on" :
             PublicVarible.Quick_trade = True 
             PromptToTelegram("xauusd trade is ON")
    except Exception as e:
            print(e)

    return
########################################################################################################
def AnalyzePositions():
    Profit = 0.0
    ProfitBuy = 0.0
    ProfitSell = 0.0
    CountBuy = 0.0
    CountSell = 0.0
    Volume = 0.0
    VolumeBuy = 0.0
    VolumeSell = 0.0
    Positions = MT5.positions_get()
    if Positions is None:
       return (Profit, ProfitBuy, ProfitSell, CountBuy, CountSell, Volume, VolumeBuy, VolumeSell)
    elif len(Positions) > 0:
         Pos = PD.DataFrame(list(Positions), columns= Positions[0]._asdict().keys())
         Profit = Pos['profit'].sum()
         ProfitBuy  = Pos.query("type == 0")['profit'].sum()
         ProfitSell = Pos.query("type == 1")['profit'].sum()
         CountBuy   = len(Pos.query("type == 0"))
         CountSell  = len(Pos.query("type == 1"))
         Volume = Pos['volume'].sum()
         VolumeBuy  = Pos.query("type == 0")['volume'].sum()
         VolumeSell = Pos.query("type == 1")['volume'].sum()

    return (Profit, ProfitBuy, ProfitSell, CountBuy, CountSell, Volume, VolumeBuy, VolumeSell)   
########################################################################################################
def CalcTotalVolumes(Pair:str):
    SumBuy = 0
    SumSell = 0
    Positions = MT5.positions_get(symbol= Pair)
    if Positions == None:
       return (round(SumBuy, 2), round(SumSell, 2))
    elif len(Positions) > 0:
         Pos = PD.DataFrame(list(Positions), columns= Positions[0]._asdict().keys())
         SumBuy += Pos.query("type == 0")['volume'].sum()
         SumSell += Pos.query("type == 1")['volume'].sum()
     
    return (round(SumBuy, 2), round(SumSell, 2))
########################################################################################################
def UpdateLastRunTime():
    Conn = pyodbc.connect(PublicVarible.ConnectionString)
    Cmd = Conn.cursor()
    Cmd.execute("UPDATE Bot SET LastRunTime = '" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f"' WHERE Id = {PublicVarible.Id}")
    Cmd.commit()
    PublicVarible.LastDatetimeRobotIsReady = datetime.now()
    Prompt("Updated last run time...")
########################################################################################################
def GetEquity():
    AccountInfo = MT5.account_info()
    if AccountInfo is None:
       Prompt("Account info is None")
       Quit()

    return AccountInfo.equity
########################################################################################################
def GetBalance():
    AccountInfo = MT5.account_info()
    if AccountInfo is None:
       Prompt("Account info is None")
       Quit()

    return AccountInfo.balance 
########################################################################################################
def CheckOrderIsOpen(Pair:str, LastCandle, TimeFrame, Type, DistanceFromLastPosition:int = 5):
    Result = False
    Positions = MT5.positions_get(symbol= Pair)
    if Positions is None:
       Result = False
    elif len(Positions) > 0:
         DF = PD.DataFrame(list(Positions),columns= Positions[0]._asdict().keys())
         DF['datetime'] = PD.to_datetime(DF['time'], unit='s')
         DF = DF.drop('time', axis=1)
         for X in range(0, len(DF), 1):
             if DF.iloc[X]['type'] == Type:
                Diff = (LastCandle['datetime'] - DF.iloc[X]['datetime']).total_seconds() / 60 / TimeFrame
                if Diff <= DistanceFromLastPosition:
                   Result = True  
    return Result
########################################################################################################
def CheckTimeFrameProcessing(Pair:str, TimeFrame, LastCalculation:str = None):
    if LastCalculation == None:
       return True
    LastRun = datetime.strptime(LastCalculation, "%H:%M")
    FloorMin1 = math.floor(LastRun.minute / 5)
    Rates = MT5.copy_rates_from_pos(Pair, TimeFrame, 0, 1)
    if Rates is not None:
       FrameRates = PD.DataFrame(Rates)
       if not FrameRates.empty:
          FrameRates['datetime'] = PD.to_datetime(FrameRates['time'], unit='s')
          FrameRates = FrameRates.drop('time', axis=1)
          FloorMin2 = math.floor(FrameRates.iloc[-1]['datetime'].minute / 5)
          if LastRun != FrameRates.iloc[-1]['datetime'].strftime("%H:%M") and FloorMin1 != FloorMin2:
             return True
          else:
             return False
       else:
          return False
    else:
          return False
########################################################################################################
def SetTimeForPair(Pair:str, TimeFrame:str, LastCalculation:str = None):
    for Item in PublicVarible.WhiteList:
             if Item['Pair'] == Pair and Item['TimeFrame'] == TimeFrame:
                if LastCalculation != None:
                   Item['LastCalculation'] = LastCalculation
########################################################################################################
def ConvertStringToTimeFrame(TimeFrame:str):
    match TimeFrame:
          case "M1": return MT5.TIMEFRAME_M1
          case "M2": return MT5.TIMEFRAME_M2
          case "M3": return MT5.TIMEFRAME_M3
          case "M4": return MT5.TIMEFRAME_M4
          case "M5": return MT5.TIMEFRAME_M5
          case "M6": return MT5.TIMEFRAME_M6
          case "M10": return MT5.TIMEFRAME_M10
          case "M12": return MT5.TIMEFRAME_M12
          case "M15": return MT5.TIMEFRAME_M15
          case "M20": return MT5.TIMEFRAME_M20
          case "M30": return MT5.TIMEFRAME_M30
          case "H1": return MT5.TIMEFRAME_H1
          case "H2": return MT5.TIMEFRAME_H2
          case "H3": return MT5.TIMEFRAME_H3
          case "H4": return MT5.TIMEFRAME_H4
          case "H6": return MT5.TIMEFRAME_H6
          case "H8": return MT5.TIMEFRAME_H8
          case "H12": return MT5.TIMEFRAME_H12
          case "D1": return MT5.TIMEFRAME_D1
          case "W1": return MT5.TIMEFRAME_W1
          case "MN1": return MT5.TIMEFRAME_MN1
########################################################################################################
def SpecifyCandleType(Open:float, Close:float):
    if Open < Close:
        return 'Bullish'
    elif Open > Close:
        return 'Bearish'
    else:
        return'Doji' 
########################################################################################################
def GetLotSize():
    AccountInfo = MT5.account_info()
    return round(AccountInfo.balance / (PublicVarible.LotIncreaseRatio * 100), 2)
########################################################################################################
def LoginAccount(Username, Password, Server, Timeout):
    Authorized = MT5.login(login= int(Username), password= Password, server= Server)
    if Authorized:
        return True
    else:
        return False
########################################################################################################
def GetTerminalInfo():
    TerminalInfo = MT5.terminal_info()
    if TerminalInfo!=None:
       Prompt("Current terminal config")
       Prompt("Connected :" + str(TerminalInfo.connected))
       Prompt("Dlls allowed :" + str(TerminalInfo.dlls_allowed))
       Prompt("Trade allowed :" + str(TerminalInfo.trade_allowed))
       Prompt("Notifications enabled :" + str(TerminalInfo.notifications_enabled))
       Prompt("Max bars :" + str(TerminalInfo.maxbars))
       Prompt("Company :" + TerminalInfo.company)
       Prompt("Name :" + TerminalInfo.name)
       Prompt("Language :" + TerminalInfo.language)
########################################################################################################
def Quit():
    MT5.shutdown()
    Prompt("MetaTrader terminal shutdown")
    PublicVarible.Executor.shutdown()
    quit()
########################################################################################################
def VisualizationPlot(FrameRates, Title, Alines, Tlines, Hlines, Vlines):
    MPF.plot(FrameRates, type='candle', style='yahoo', alines= Alines, hlines= Hlines, title= Title, savefig= 'Images/' + str(uuid.uuid1()) + '.png')# dict(alines= Alines,colors=['r'],linewidths=(0.7)), vlines=dict(vlines=Vlines,alpha=0.2), title= Title, savefig= 'Images/' + str(uuid.uuid1()) + '.png')
########################################################################################################
def Botdashboard(status,Pair:str) : 
    match status : 
          case 1 : print(Fore.LIGHTYELLOW_EX,"Market is open and sterategy V7 is",Fore.LIGHTGREEN_EX,"                     Runing",Fore.RESET,"\n")
          case 2 : 
                   print(Fore.YELLOW,"Terminal is turn on and market    ",Fore.LIGHTRED_EX,"                     No Tick",Fore.RESET,"\n")
                   print(Fore.YELLOW,"Terminal is turn on, sterategy is ",Fore.LIGHTRED_EX,"                     Stoped",Fore.RESET,"\n")
          case 4 : print(Fore.YELLOW,"Allowed working hours             ",Fore.LIGHTRED_EX,"                     No",Fore.RESET,"\n")
          case 7 : print(Fore.LIGHTYELLOW_EX,"Allowed working hours             ",Fore.LIGHTGREEN_EX,"                     Yes",Fore.RESET,"\n")
          case 5 : print(Fore.YELLOW,"Average true range (ATR)          ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n")
          case 6 : print(Fore.LIGHTYELLOW_EX,"Average true range (ATR)          ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 8 : print(Fore.LIGHTYELLOW_EX,"Market trend status               ",Fore.LIGHTRED_EX,"                     On border",Fore.RESET,"\n")
          case 9 : print(Fore.LIGHTYELLOW_EX,"Market trend status               ",Fore.LIGHTGREEN_EX,"                     No direction",Fore.RESET,"\n")
          case 10: print(Fore.LIGHTYELLOW_EX,"Market trend status               ",Fore.LIGHTGREEN_EX,"                     Directional",Fore.RESET,"\n")
          #case 3 : 
          #         Positions = MT5.positions_get(symbol= Pair)
          #         if Positions is None:
          #            return
          #         elif len(Positions) > 0:
          #            Pos = PD.DataFrame(list(Positions), columns= Positions[0]._asdict().keys())
          #            Profit = Pos['profit'].sum()
          #            if Profit >= 0 :
          #               
          #               print(Fore.LIGHTYELLOW_EX,"Total profit at this moment     ",Fore.LIGHTGREEN_EX,"                      ",round(Profit,2),Fore.RESET,"\n")
          #            else :
          #                
          #           #     print(Fore.LIGHTYELLOW_EX,"Total profit at this moment     ",Fore.LIGHTRED_EX,"                     ",round(Profit,2),Fore.RESET,"\n")
          #           # print(Fore.LIGHTYELLOW_EX,"The remaining distance to the loss",Fore.LIGHTRED_EX,"                   ",round(space, 2),Fore.RESET,"\n")
          #           # print(Fore.LIGHTYELLOW_EX,"Traling TakeProfit                ",Fore.YELLOW,"                    ",round(PublicVarible.TrailingTP, 2),Fore.RESET,"\n")
          case 11 : print(Fore.YELLOW,"Stochastic M30 status             ",Fore.LIGHTRED_EX,"                     oversold",Fore.RESET,"\n")   ; #write_None(Pair,text = "Stochastic M30 status")
          case 12 : print(Fore.YELLOW,"Stochastic M30 status             ",Fore.LIGHTRED_EX,"                     overbought",Fore.RESET,"\n") ; #write_None(Pair,text = "Stochastic M30 status")
                    
          case 13 : 
                    print(Fore.LIGHTYELLOW_EX,"Super trend M5                                        ",Back.RED,Fore.LIGHTWHITE_EX," DOWN",Fore.RED,"|",Back.RESET,Fore.RESET)
                    print(Fore.WHITE ,"---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----",Fore.RESET)
          case 23 : 
                    print(Fore.LIGHTYELLOW_EX,"Super trend M5                                        ",Back.GREEN,Fore.LIGHTWHITE_EX,"   UP",Fore.GREEN,"|",Back.RESET,Fore.RESET)
                    print(Fore.WHITE ,"---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----",Fore.RESET)
          case 14 : print(Fore.LIGHTYELLOW_EX,"Market is open and sterategy V8 is",Fore.LIGHTGREEN_EX,"                     Runing",Fore.RESET,"\n")
          #case 15 : print(Fore.LIGHTYELLOW_EX,"sum of sell volumes               ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          #case 24 : print(Fore.YELLOW,"Sum of buy volumes                ",Fore.LIGHTRED_EX,"                     Oversize",Fore.RESET,"\n")
          #case 25 : print(Fore.LIGHTYELLOW_EX,"Sum of buy volumes                ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          #case 16 : print(Fore.YELLOW,"Interval between sell orders      ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n")
          #case 17 : print(Fore.LIGHTYELLOW_EX,"Interval between sell orders      ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          #case 26 : print(Fore.YELLOW,"Interval between buy orders       ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n")
          case 27 : 
                    print(Fore.YELLOW,"Finding swing                     ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Finding swing")
                    #write_None(Pair,text = "Stochastic M30 status")
          case 18 : print(Fore.LIGHTYELLOW_EX,"Stoch-RSI sell signal             ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 19 : print(Fore.YELLOW,"Stoch-RSI sell signal             ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Stoch-RSI sell signal")
          case 20 : print(Fore.YELLOW,"Finding swing high                ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Finding swing high")
          case 33 : print(Fore.LIGHTYELLOW_EX,"Finding swing high                ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 29 : print(Fore.LIGHTYELLOW_EX,"SymbolInfo.spread                 ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 30 : print(Fore.YELLOW," SymbolInfo.spread                ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "SymbolInfo.spread")
          case 28 : print(Fore.YELLOW,"Finding swing low                 ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Finding swing low ")
          case 34 : print(Fore.LIGHTYELLOW_EX,"Finding swing low                 ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 21 : print(Fore.YELLOW,"Sell signal ...                   ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n")
          case 31 : print(Fore.YELLOW,"TP  is LOW ...                    ",Fore.LIGHTRED_EX,"                     Returned",Fore.RESET,"\n")
          case 22 :
                    print(Fore.LIGHTYELLOW_EX,"Super trend H1                                        ",Back.GREEN,Fore.LIGHTWHITE_EX,"   UP",Fore.GREEN,"|",Back.RESET,Fore.RESET)

          case 32 :
                    print(Fore.LIGHTYELLOW_EX,"Super trend H1                                        ",Back.RED,Fore.LIGHTWHITE_EX," DOWN",Fore.RED,"|",Back.RESET,Fore.RESET)
          case 35 : print(Fore.YELLOW,"ADX is LOW ...                    ",Fore.LIGHTRED_EX,"                     Returned",Fore.RESET,"\n")
          case 36 : print(Fore.YELLOW,"Limit daily target or manual stop ",Fore.LIGHTRED_EX,"                     YES",Fore.RESET,"\n")
          case 37 : 
                    SymbolInfo = MT5.symbol_info(Pair)
                    if SymbolInfo is not None:
                       price = (SymbolInfo.bid + SymbolInfo.ask) / 2
                       print(Fore.YELLOW,"Is the price close to important levels?",Fore.LIGHTRED_EX,"                YES ",round(price,2),Fore.RESET,"\n")
                    else :  print(Fore.YELLOW,"Is the price close to important levels?",Fore.LIGHTRED_EX,"                YES ....",Fore.RESET,"\n")
          case 38 : print(Fore.YELLOW,"Price gap with previous sell            ",Fore.LIGHTRED_EX,"               is low ",Fore.RESET,"\n")
          case 39 : print(Fore.LIGHTYELLOW_EX,"Price gap with previous sell            ",Fore.LIGHTGREEN_EX,"               is OK ",Fore.RESET,"\n")
          case 40 : print(Fore.YELLOW,"Price gap with previous buy             ",Fore.LIGHTRED_EX,"               is low ",Fore.RESET,"\n")
          case 41 : print(Fore.LIGHTYELLOW_EX,"Price gap with previous buy             ",Fore.LIGHTGREEN_EX,"               is OK ",Fore.RESET,"\n")
          case 42 : print(Fore.YELLOW,"money flow index (MFI) satus            ",Fore.LIGHTRED_EX,"               overbought",Fore.RESET,"\n") ; write_None(Pair,text = "money flow index (MFI) satus ")
          case 43 : print(Fore.YELLOW,"money flow index (MFI) satus            ",Fore.LIGHTRED_EX,"               oversold",Fore.RESET,"\n") ; write_None(Pair,text = "money flow index (MFI) satus ")
          #case 44 : print(Fore.LIGHTYELLOW_EX,"Emergrncy buy                   ",Fore.LIGHTGREEN_EX,"             Active ",Fore.RESET,"\n")
          #case 45 : print(Fore.LIGHTYELLOW_EX,"Emergrncy sell                  ",Fore.LIGHTGREEN_EX,"             Active ",Fore.RESET,"\n")
          #case 46 : print(Fore.LIGHTRED_EX,"emergency mode lower -0.05            ",Fore.LIGHTRED_EX,  "                 TP = None !!!",Fore.RESET,"\n")  ##*******جدید***********
          case 47 : print(Fore.YELLOW,"Internal ST No Direction             ",Fore.LIGHTRED_EX,  "                  Wait ...",Fore.RESET,"\n")
          case 48 : print(Fore.LIGHTYELLOW_EX,"M5 RSI sell signal                ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 49 : print(Fore.YELLOW,"M5 RSI sell signal                ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "M5 RSI sell signal  ")
          case 50 : print(Fore.LIGHTYELLOW_EX,"M5 RSI buy signal                 ",Fore.LIGHTGREEN_EX,"                     OK",Fore.RESET,"\n")
          case 51 : print(Fore.YELLOW,"M5 RSI buy signal                 ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "M5 RSI buy signal  ")
          #case 52 : print(Fore.YELLOW,"Today Loss is Over                ",Fore.LIGHTRED_EX,"                     Sorry !",Fore.RESET,"\n")
          case 52 : print(Fore.YELLOW,"Posision SL is Over               ",Fore.LIGHTRED_EX,"                     Sorry !",Fore.RESET,"\n")
          case 53 : print(Fore.YELLOW,"Posision Buy is Open              ",Fore.LIGHTRED_EX,"                     Sorry !",Fore.RESET,"\n")
          case 54 : print(Fore.YELLOW,"Posision Sell is Open             ",Fore.LIGHTRED_EX,"                     Sorry !",Fore.RESET,"\n")
          case 55 : print(Fore.LIGHTYELLOW_EX,"RSI Negative Slope (<-0.5)         ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 57 : print(Fore.LIGHTYELLOW_EX,"RSI Positive Slope (>+0.5)         ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 56 : print(Fore.YELLOW,"RSI Negative Slope (<-0.5)         ",Fore.LIGHTRED_EX,"                    Not OK",Fore.RESET,"\n") 
          case 58 : print(Fore.YELLOW,"RSI Positive Slope (>+0.5)         ",Fore.LIGHTRED_EX,"                    Not OK",Fore.RESET,"\n")
          case 59 : print(Fore.LIGHTYELLOW_EX,"STH30 Negative Slope (-)           ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 60 : print(Fore.LIGHTYELLOW_EX,"STH30 Positive Slope (+)           ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 61 : print(Fore.YELLOW,"STH30 Negative Slope (-)           ",Fore.LIGHTRED_EX,"                    Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "STH30 Negative Slope (-) ")
          case 62 : print(Fore.YELLOW,"STH30 Positive Slope (+)           ",Fore.LIGHTRED_EX,"                    Not OK",Fore.RESET,"\n"); #write_None(Pair,text = "STH30 Positive Slope (+)")
          case 63 : print(Fore.LIGHTYELLOW_EX,"Super Trend M15 Sell Allow         ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 64 : print(Fore.YELLOW,"Super Trend M15 Sell Allow         ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Super Trend M15 Sell Allow")
          case 65 : print(Fore.LIGHTYELLOW_EX,"Super Trend M15 Buy Allow          ",Fore.LIGHTGREEN_EX,"                    is OK",Fore.RESET,"\n")
          case 66 : print(Fore.YELLOW,"Super Trend M15 Buy Allow          ",Fore.LIGHTRED_EX,"                     Not OK",Fore.RESET,"\n") ; #write_None(Pair,text = "Super Trend M15 Buy Allow")

    return(True)

########################################################################################################
def DailyProfitControl(Pair:str) :
        
    Profit = 0
    HProfit = 0
    From = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0)
    To = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23, 59, 59)
  
    HistoryOrders= MT5.history_deals_get(From , To)
    if HistoryOrders == None:
       HProfit = 0
    elif len(HistoryOrders) > 0:
       DF = PD.DataFrame(list(HistoryOrders), columns= HistoryOrders[0]._asdict().keys())
       HProfit = DF['profit'].sum()
     
    Positions = MT5.positions_get(symbol= Pair)
    if Positions is None:
        return
    elif len(Positions) > 0:
          Pos = PD.DataFrame(list(Positions), columns= Positions[0]._asdict().keys())
          Profit = Pos['profit'].sum()
    
    #print("HProfit ",HProfit," Profit",Profit , "Profit =" , HProfit + Profit)

    Balance = GetBalance()
    if Balance >= 1000:
        A =  Balance // 1000
        Balance = round(A * 1000)

    if (HProfit + Profit) > (PublicVarible.targetProfit * Balance) and PublicVarible.CanOpenOrderST == True : 
       MT5.Close(symbol= Pair)
       PublicVarible.CanOpenOrderST = False
       Prompt(f"Daily profit target has been touched and All orders successfully closed, Balance: {str(GetBalance())}$")
       PromptToTelegram(Text= f"Daily profit target has been touched and All orders successfully closed" + "\n" + f"💰 Balance: {str(GetBalance())}$")
    return(True)
########################################################################################################
def importantprice(Pair:str, PriceST2 , PriceST3) : 
    SymbolInfo = None
    if Pair is not None:
       SymbolInfo = MT5.symbol_info(Pair)
    
    price = (SymbolInfo.bid + SymbolInfo.ask) / 2 

    if SymbolInfo.name == 'XAUUSDb' : 
        levelupST1 = PriceST2 + (150 * SymbolInfo.point)
        leveldownST1 = PriceST2 - (150 * SymbolInfo.point)
        levelupST4 = PriceST3 + (100 * SymbolInfo.point)
        leveldownST4 = PriceST3 - (100 * SymbolInfo.point)
        if SymbolInfo is not None:
           for i in range(30) : 
              levelup = (i * 100) + (150 * SymbolInfo.point)
              leveldown = (i * 100) - (150 * SymbolInfo.point) 
              if price < levelup and price > leveldown : 
                 return(False) 
    else : 
        levelupST1 = PriceST2 + (20 * SymbolInfo.point)
        leveldownST1 = PriceST2 - (20 * SymbolInfo.point)
        levelupST4 = PriceST3 + (10 * SymbolInfo.point)
        leveldownST4 = PriceST3 - (10 * SymbolInfo.point)

    if (price < levelupST1 and price > leveldownST1) or (price < levelupST4 and price > leveldownST4) or (price < 2002 and price > 1998 ) or (price < 1502 and price > 1498 ) : 
           return(False)
    else : return(True)
########################################################################################################

from numpy import datetime_data, nan as npNaN
from pandas import DataFrame
from pandas_ta.overlap import hl2
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, verify_series

def supertrend(Pair , high, low, close, length=None, multiplier=None, offset=None, **kwargs):
    """Indicator: Supertrend"""
    # Validate Arguments
    SymbolInfo = MT5.symbol_info(Pair)
    length = int(length) if length and length > 0 else 7
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None: return

    # Calculate Results
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [npNaN] * m, [npNaN] * m

    hl2_ = hl2(high, low)
    matr = multiplier * atr(high, low, close, length)
    upperband = hl2_ + matr
    lowerband = hl2_ - matr

    for i in range(1, m):
        if close.iloc[i] > upperband.iloc[i - 1] and close.iloc[i - 1] > upperband.iloc[i - 1] and close.iloc[i] > high.iloc[i - 1] :
              dir_[i] = 1
        elif close.iloc[i] > (upperband.iloc[i - 1] + (20 * SymbolInfo.point)) : 
              dir_[i] = 1

        elif close.iloc[i] < lowerband.iloc[i - 1] and close.iloc[i - 1] < lowerband.iloc[i - 1] and close.iloc[i] < high.iloc[i - 1] :
              dir_[i] = -1
        elif close.iloc[i] < (lowerband.iloc[i - 1] - (20 * SymbolInfo.point)) : 
              dir_[i] = -1

        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lowerband.iloc[i]
        else:
            trend[i] = short[i] = upperband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"SUPERT{_props}": trend,
            f"SUPERTd{_props}": dir_,
            f"SUPERTl{_props}": long,
            f"SUPERTs{_props}": short,
        }, index=close.index)

    df.name = f"SUPERT{_props}"
    df.category = "overlap"

    # Apply offset if needed
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    if "fill_method" in kwargs:
        df.fillna(method=kwargs["fill_method"], inplace=True)

    return df

def supertrendH(Pair , high, low, close, length=None, multiplier=None, offset=None, **kwargs):
    """Indicator: Supertrend H1 & H4 """
    # Validate Arguments
    SymbolInfo = MT5.symbol_info(Pair)
    length = int(length) if length and length > 0 else 7
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None: return

    # Calculate Results
    m = close.size
    dir_, trend = [1] * m, [0] * m
    long, short = [npNaN] * m, [npNaN] * m

    hl2_ = hl2(high, low)
    matr = multiplier * atr(high, low, close, length)
    upperband = hl2_ + matr
    lowerband = hl2_ - matr

    for i in range(1, m):
        if close.iloc[i] > upperband.iloc[i - 1] and close.iloc[i - 1] > upperband.iloc[i - 1] and close.iloc[i] > high.iloc[i - 1] :
              dir_[i] = 1
        elif close.iloc[i] > (upperband.iloc[i - 1] + (100 * SymbolInfo.point)) : 
              dir_[i] = 1

        elif close.iloc[i] < lowerband.iloc[i - 1] and close.iloc[i - 1] < lowerband.iloc[i - 1] and close.iloc[i] < high.iloc[i - 1] :
              dir_[i] = -1
        elif close.iloc[i] < (lowerband.iloc[i - 1] - (100 * SymbolInfo.point)) : 
              dir_[i] = -1

        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
                lowerband.iloc[i] = lowerband.iloc[i - 1]
            if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
                upperband.iloc[i] = upperband.iloc[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lowerband.iloc[i]
        else:
            trend[i] = short[i] = upperband.iloc[i]

    # Prepare DataFrame to return
    _props = f"_{length}_{multiplier}"
    df = DataFrame({
            f"SUPERT{_props}": trend,
            f"SUPERTd{_props}": dir_,
            f"SUPERTl{_props}": long,
            f"SUPERTs{_props}": short,
        }, index=close.index)

    df.name = f"SUPERT{_props}"
    df.category = "overlap"

    # Apply offset if needed
    if offset != 0:
        df = df.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        df.fillna(kwargs["fillna"], inplace=True)

    if "fill_method" in kwargs:
        df.fillna(method=kwargs["fill_method"], inplace=True)

    return df

supertrend.__doc__ = \
""" text"""
#######################################################################################
    
def get_sell_positions_with_open_prices():
    # دریافت تمام موقعیت‌های باز
    open_positions = MT5.positions_get()

    # فیلتر کردن تیکت‌های موقعیت‌های فروش
    sell_positions = [position for position in open_positions if position.type == MT5.POSITION_TYPE_SELL]

    # ساخت یک دیکشنری برای نگهداری تیکت و قیمت باز شدن هر موقعیت فروش
    sell_positions_with_open_prices = {position.ticket: position.price_open for position in sell_positions}

    return sell_positions_with_open_prices

def get_buy_positions_with_open_prices():
    # دریافت تمام موقعیت‌های باز
    open_positions = MT5.positions_get()

    if open_positions is None:
        print("⚠️  MT5.positions_get() returned None — احتمالاً متاتریدر وصل نیست یا حساب فعال نداری.")
        return {}

    # فیلتر کردن موقعیت‌های خرید
    buy_positions = [position for position in open_positions if position.type == MT5.POSITION_TYPE_BUY]

    # ساخت دیکشنری شامل تیکت و قیمت باز شدن
    buy_positions_with_open_prices = {position.ticket: position.price_open for position in buy_positions}

    return buy_positions_with_open_prices

########################################################################################

def write_trade_info_to_file(Pair ,Pos, EntryPrice, SL, TP1, Direction ):
    file_path = 'C:/logTrade.txt'  # مسیر فایل
    with open(file_path, 'a') as file:
        file.write("Pair: {}\n".format(Pair))
        file.write("Pos: {}\n".format(Pos))
        file.write("EntryPrice : {}\n".format(EntryPrice))
        file.write("SL: {}\n".format(SL))
        file.write("TP1: {}\n".format(TP1))
        file.write("Direction: {}\n".format(Direction))
        file.write("-" * 30 + "\n")  
########################################################################################

def write_None(Pair ,text ):
    file_path = 'C:/logNone.txt'  # مسیر فایل
    with open(file_path, 'a') as file:
        file.write("{}, {}\n".format(Pair, text))
        #file.write("-" * 30 + "\n")  
        
# Define the custom font using @ or any other characters
########################################################################################

custom_font = {
    'A': ["  @  ", " @ @ ", "@@@@@", "@   @", "@   @"],
    'B': ["@@@@ ", "@   @", "@@@@ ", "@   @", "@@@@ "],
    'C': [" @@@ ", "@   @", "@    ", "@   @", " @@@ "],
    'D': ["@@@@ ", "@   @", "@   @", "@   @", "@@@@ "],
    'E': ["@@@@@", "@    ", "@@@@ ", "@    ", "@@@@@"],
    'F': ["@@@@@", "@    ", "@@@@ ", "@    ", "@    "],
    'G': [" @@@ ", "@    ", "@ @@@", "@   @", " @@@ "],
    'H': ["@   @", "@   @", "@@@@@", "@   @", "@   @"],
    'I': [" @@@ ", "  @  ", "  @  ", "  @  ", " @@@ "],
    'J': ["  @@@", "   @ ", "   @ ", "@  @ ", " @@  "],
    'K': ["@   @", "@  @ ", "@@@  ", "@  @ ", "@   @"],
    'L': ["@    ", "@    ", "@    ", "@    ", "@@@@@"],
    'M': ["@   @", "@@ @@","@ @ @", "@   @", "@   @"],
    'N': ["@   @", "@@  @", "@ @ @", "@  @@", "@   @"],
    'O': [" @@@ ", "@   @", "@   @", "@   @", " @@@ "],
    'P': ["@@@@ ", "@   @", "@@@@ ", "@    ", "@    "],
    'Q': [" @@@ ", "@   @", "@   @", "@  @@", " @@@@"],
    'R': ["@@@@ ", "@   @", "@@@@ ", "@  @ ", "@   @"],
    'S': [" @@@@", "@    ", " @@@ ", "    @", "@@@@ "],
    'T': ["@@@@@", "  @  ", "  @  ", "  @  ", "  @  "],
    'U': ["@   @", "@   @", "@   @", "@   @", " @@@ "],
    'V': ["@   @", "@   @", "@   @", " @@@ ", "  @  "],
    'W': ["@   @", "@   @", "@ @ @", "@@@@@", "@   @"],
    'X': ["@   @", " @ @ ", "  @  ", " @ @ ", "@   @"],
    'Y': ["@   @", " @ @ ", "  @  ", "  @  ", "  @  "],
    'Z': ["@@@@@", "   @ ", "  @  ", " @   ", "@@@@@"]
}

def print_custom_text(text):
    print(Back.LIGHTCYAN_EX,"",Fore.RED,"","\n")
    text = text.upper()
    for row in range(5):  # 5 rows for each letter in the custom font
        line = ""
        for char in text:
            if char in custom_font:
                line += custom_font[char][row] + "  "
            else:
                line += "     "  # space for unknown characters
        print(line)
########################################################################################
        
def get_all_buy_positions(Pair):
    from_date = datetime.now() - timedelta(minutes=20)
    all_positions = MT5.history_orders_get(from_date, datetime.now() , group = Pair)
    print("all_positions: ",all_positions)
    if all_positions is not None:
         # فیلتر کردن تیکت‌های موقعیت‌های خرید و فروش
         buy_positions = [position for position in all_positions if position.type == MT5.POSITION_TYPE_BUY]
         sell_positions = [position for position in all_positions if position.type == MT5.POSITION_TYPE_SELL]
         all_buy_positions = buy_positions + sell_positions
         
         return all_buy_positions

########################################################################################

def send_telegram_messages(text, chat_ids):
    token = "8041867463:AAEUH_w2CYFne521LxNVsuR6hiuqk-75pfQ"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    responses = {}
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        responses[chat_id] = response.json()
    return responses

########################################################################################

def telalert() :
    current_datetime = datetime.now()
    restricted_hours = {9}
    if (current_datetime.weekday() == 5) and  (current_datetime.minute == 0) and (current_datetime.second < 2) and (current_datetime.hour in restricted_hours):
      Text = f"⚠️ توجه ⚠️ \n امروز شنبه مورخ {jdatetime.datetime.now().strftime('%Y-%m-%d')}  بازارهای جهانی فارکس و طلا #تعطیل است"
      results = send_telegram_messages(Text, PublicVarible.chat_ids)
    elif (current_datetime.weekday() == 6) and  (current_datetime.minute == 0) and (current_datetime.second < 2) and (current_datetime.hour in restricted_hours):
      Text = f"⚠️ توجه ⚠️ \n امروز یکشنبه مورخ {jdatetime.datetime.now().strftime('%Y-%m-%d')}  بازارهای جهانی فارکس و طلا #تعطیل است"
      results = send_telegram_messages(Text, PublicVarible.chat_ids) 
    elif (current_datetime.weekday() == 6) and  (current_datetime.minute == 0) and (current_datetime.second < 2) and (current_datetime.hour == 21):
      Text = f"⛔⚠️ توجه ⚠️⛔ \n فردا دوشنبه است و از ساعاتی دیگر بازار باز میشود! حتما #اخبار هفته جاری را مرور کنید"
      results = send_telegram_messages(Text, PublicVarible.chat_ids) 
    elif (current_datetime.weekday() == 4) and  (current_datetime.minute == 0) and (current_datetime.second < 2) and (current_datetime.hour == 21):
      Text = f"⛔⚠️ توجه ⚠️⛔ \n امروز جمعه مورخ {jdatetime.datetime.now().strftime('%Y-%m-%d')} شب آخر بازار است . لطفا معاملات باز خود را مدیریت کنید"
      results = send_telegram_messages(Text, PublicVarible.chat_ids)  

########################################################################################

def delete_all_limit_orders():
    """
    حذف تمامی سفارش‌های لیمیت (BUY_LIMIT و SELL_LIMIT) که هنوز اجرا نشده‌اند.
    """
    # دریافت لیست سفارش‌های باز
    orders = MT5.orders_get()
    if orders:
        for order in orders:
            # بررسی نوع سفارش (فقط لیمیت‌ها حذف شوند)
            if order.type in (MT5.ORDER_TYPE_BUY_LIMIT, MT5.ORDER_TYPE_SELL_LIMIT):
                request = {
                    "action": MT5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                result = MT5.order_send(request)

                if result.retcode == MT5.TRADE_RETCODE_DONE:
                    print(f"سفارش {order.ticket} با موفقیت حذف شد.")
                else:
                    print(f"خطا در حذف سفارش {order.ticket}: {result.comment}")
    else:
        print("هیچ سفارش لیمیتی برای حذف وجود ندارد.")


def has_pending_limit_orders():
    """
    بررسی می‌کند که آیا سفارش لیمیت (BUY_LIMIT یا SELL_LIMIT) باز وجود دارد یا نه.
    در صورت وجود، مقدار True باز می‌گرداند و در غیر اینصورت False.
    """
    # دریافت لیست سفارش‌های باز
    orders = MT5.orders_get()

    if orders:
        # بررسی سفارشات لیمیت
        for order in orders:
            if order.type in (MT5.ORDER_TYPE_BUY_LIMIT, MT5.ORDER_TYPE_SELL_LIMIT):
                return True  # اگر سفارش لیمیت پیدا شد، مقدار True باز می‌گرداند
    return False  # اگر هیچ سفارش لیمیتی وجود نداشت، مقدار False باز می‌گرداند


########################################################################################

def plot_candles_and_send_telegram(FrameRatesM5, pair, Text):
    """
    رسم نمودار کندل‌ها و ارسال آن به تلگرام
    
    Args:
        FrameRatesM5 (DataFrame): دیتافریم حاوی اطلاعات کندل‌ها
        pair (str): نام جفت ارز
        Text (str): متن توضیحات برای کپشن تصویر
    """
    try:
        # بررسی وجود ستون‌های مورد نیاز
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in FrameRatesM5.columns for col in required_columns):
            error_msg = "Warning: Missing required columns in DataFrame"
            print(error_msg)
            send_telegram_messages(error_msg, PublicVarible.chat_ids)
            return False

        # تبدیل و تنظیم اندیس به datetime
        if 'datetime' in FrameRatesM5.columns:
            FrameRatesM5['datetime'] = pd.to_datetime(FrameRatesM5['datetime'])
            FrameRatesM5.set_index('datetime', inplace=True)

        # حذف مقادیر NaN
        FrameRatesM5.dropna(subset=required_columns, inplace=True)

        # تنظیم استایل نمودار
        mc = mpf.make_marketcolors(up='g', down='r', edge='inherit', wick='inherit', volume='inherit')
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='')

        # ذخیره نمودار در بافر
        buf = BytesIO()
        mpf.plot(FrameRatesM5, 
                type='candle',
                style=s,
                title=f'Candlestick Chart - {pair}',
                savefig=dict(fname=buf, dpi=300, bbox_inches='tight'))
        buf.seek(0)
        
        # ارسال تصویر به تلگرام
        send_telegram_photo(buf, PublicVarible.chat_ids, Text)
        return True
        
    except Exception as e:
        error_msg = f"Error in plot_candles_and_send_telegram: {str(e)}"
        print(error_msg)
        send_telegram_messages(error_msg, PublicVarible.chat_ids)
        return False

########################################################################################

def send_telegram_photo(photo_buffer, chat_ids, caption=""):
    print(f"Received chat_ids: {chat_ids}, Type: {type(chat_ids)}")  # بررسی مقدار

    TOKEN = "8041867463:AAGad64rvG7qQ2AVdF6xrCnGvtyU-1iFE4U"
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    responses = {}

    for chat_id in chat_ids:
        #print(f"Processing chat_id: {chat_id}, Type: {type(chat_id)}")  # بررسی مقدار در حلقه
        
        photo_buffer.seek(0)  # بازگرداندن موقعیت بافر به ابتدا
        files = {'photo': ('chart.png', photo_buffer, 'image/png')}
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, files=files, data=data)
        
        responses[chat_id] = response.json()
    
    return responses


########################################################################################""""
import numpy as np
import pandas_ta as PTA

def analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30):
    """
    تحلیل قدرت بازار با استفاده از سه تایم‌فریم (M5, M15, M30)
    خروجی:
        signal: +1 (قدرت خریداران)، -1 (قدرت فروشندگان)، 0 (عدم قطعیت)
        confidence_score: ضریب اطمینان به صورت درصد که نشان‌دهنده دقت سیگنال است.
    """

    def find_divergence(prices, indicator_values):
        """
        بررسی واگرایی بین قیمت و اندیکاتور
        """
        price_peaks, price_troughs = find_peaks_and_troughs(prices)
        indicator_peaks, indicator_troughs = find_peaks_and_troughs(indicator_values)

        bullish_divergence = False
        bearish_divergence = False

        if price_troughs and indicator_troughs and len(price_troughs) >= 2 and len(indicator_troughs) >= 2:
            if prices[price_troughs[-1]] < prices[price_troughs[-2]] and indicator_values[indicator_troughs[-1]] > indicator_values[indicator_troughs[-2]]:
                bullish_divergence = True

        if price_peaks and indicator_peaks and len(price_peaks) >= 2 and len(indicator_peaks) >= 2:
            if prices[price_peaks[-1]] > prices[price_peaks[-2]] and indicator_values[indicator_peaks[-1]] < indicator_values[indicator_peaks[-2]]:
                bearish_divergence = True

        return bullish_divergence, bearish_divergence

    def find_peaks_and_troughs(values):
        """
        یافتن قله‌ها و کف‌ها در یک سری زمانی
        """
        peaks = []
        troughs = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] > values[i + 1]:
                peaks.append(i)
            if values[i] < values[i - 1] and values[i] < values[i + 1]:
                troughs.append(i)
        return peaks, troughs

    def single_tf_analysis(FrameRates):
        try:
            # 1. حجم
            volume_bullish = 0
            volume_bearish = 0
            for i in range(-7, -1):
                if FrameRates.iloc[i]['close'] > FrameRates.iloc[i]['open']:
                    volume_bullish += FrameRates.iloc[i]['tick_volume']
                else:
                    volume_bearish += FrameRates.iloc[i]['tick_volume']
            volume_ratio = volume_bullish / (volume_bearish + 1)
            volume_signal = 1 if volume_ratio > 1.2 else (-1 if volume_ratio < 0.8 else 0)

            # 2. مومنتوم
            changes = [FrameRates.iloc[i]['close'] - FrameRates.iloc[i-1]['close'] for i in range(-6, 0)]
            avg_change = sum(changes) / len(changes)
            momentum_signal = 1 if avg_change > 0 else (-1 if avg_change < 0 else 0)

            # 3. RSI + واگرایی
            rsi = PTA.rsi(FrameRates['close'], length=14)
            rsi_value = rsi.iloc[-2]
            rsi_signal = 1 if rsi_value > 60 else (-1 if rsi_value < 40 else 0)
            bullish_div_rsi, bearish_div_rsi = find_divergence(FrameRates['close'], rsi)
            if bullish_div_rsi:
                rsi_signal = 1
            elif bearish_div_rsi:
                rsi_signal = -1

            # 4. EMA
            ema = FrameRates['close'].ewm(span=20, adjust=False).mean()
            ema_signal = 1 if FrameRates.iloc[-2]['close'] > ema.iloc[-2] else -1

            # 5. OBV + واگرایی
            obv = PTA.obv(FrameRates['close'], FrameRates['tick_volume'])
            obv_diff = obv.iloc[-2] - obv.iloc[-7]
            obv_signal = 1 if obv_diff > 0 else -1
            bullish_div_obv, bearish_div_obv = find_divergence(FrameRates['close'], obv)
            if bullish_div_obv:
                obv_signal = 1
            elif bearish_div_obv:
                obv_signal = -1

            # 6. بررسی قدرت کندل‌ها (لنس بگز)
            strong_bullish = 0
            strong_bearish = 0
            for i in range(-6, -1):
                row = FrameRates.iloc[i]
                height = row['high'] - row['low']
                if height == 0:
                    continue
                close_pos = (row['close'] - row['low']) / height
                if close_pos > 2/3:
                    strong_bullish += 1
                elif close_pos < 1/3:
                    strong_bearish += 1
            if strong_bullish >= 3:
                price_action_signal = 1
            elif strong_bearish >= 3:
                price_action_signal = -1
            else:
                price_action_signal = 0

            # ترکیب سیگنال‌ها
            signals = [volume_signal, momentum_signal, rsi_signal, ema_signal, obv_signal, price_action_signal]
            bullish = signals.count(1)
            bearish = signals.count(-1)

            # ضریب اطمینان
            weighted_signals = sum(signals)
            total_weight = len(signals)
            confidence_score = weighted_signals / total_weight

            if bullish >= 3:
                return 1, confidence_score
            elif bearish >= 3:
                return -1, confidence_score
            else:
                return 0, confidence_score

        except Exception as e:
            print(f"[Error in single_tf_analysis]: {str(e)}")
            return 0, 0

    # تحلیل سه تایم‌فریم
    signal_M5, conf_M5 = single_tf_analysis(FrameRatesM5)
    signal_M15, conf_M15 = single_tf_analysis(FrameRatesM15)
    signal_M30, conf_M30 = single_tf_analysis(FrameRatesM30)

    # محاسبه نمره نهایی با وزن‌دهی: M30 (2), M15 (1.5), M5 (1)
    final_score = (2 * signal_M30 + 1.5 * signal_M15 + 1 * signal_M5) / 4.5
    final_confidence = (2 * conf_M30 + 1.5 * conf_M15 + 1 * conf_M5) / 4.5

    # تبدیل به درصد (0 تا 100)
    final_confidence_percent = abs(final_confidence * 100)

    # صدور تصمیم نهایی
    if final_score > 0.5:
        return 1, final_confidence_percent  # خریداران با اطمینان
    elif final_score < -0.5:
        return -1, final_confidence_percent  # فروشندگان با اطمینان
    else:
        return 0, final_confidence_percent  # بدون سیگنال واضح


########################################################################################""""

def time_to_trade(Pair:str):
    SymbolInfo = MT5.symbol_info(Pair)
    current_time = time.time()
    current_datetime = datetime.now()
    #print(f"{Pair} Price is ({SymbolInfo.ask} $)")
    restricted_hours = {6 , 11 , 13 , 19 , 16}
    if current_datetime.minute == 0 and current_datetime.hour in restricted_hours:
            #PublicVarible.CanOpenOrder = False
            #PublicVarible.risk = 
            if current_time - PublicVarible.last_execution_timeAll >= 600 :
                   Text = f"⏰ Time : {current_datetime} \n"
                   Text += f"Risk changed to Safe Mode 🟢 (Low) \n"
                   Text += f"Can Open Order Stoped ... \n"
                   Text += f"{Pair} Price is ({SymbolInfo.ask} $)"
                   PromptToTelegram(Text)
                   PublicVarible.last_execution_timeAll = current_time
                         
            # if current_datetime.minute == 0 and current_datetime.hour in {13 , 19}:
            #    Text = f"⚠️هشدار⚠️ \n اطلاعات ارائه شده در این بات ، صرفا جنبه #آموزشی داشته و سازنده مسئولیتی در قبال ضرر احتمالی  ندارد . لطفا اصول حرفه ای معامله و مدیریت سرمایه را رعایت فرمائید . "
            #    results = send_telegram_messages(Text, PublicVarible.chat_ids)

##################################################################################################

# def get_signal_from_model(pair):
#     """
#     Get prediction signals from three different models and combine them
    
#     Args:
#         pair: Currency pair
        
#     Returns:
#         Tuple[float, float, float]: Prediction signals from three models
#     """
#     try:
#         # Create predictor instances
#         predictor = GoldPricePredictor(pair, days=30)
#         predictorM5 = GoldPricePredictorM5(pair, days=7)
#         predictorM5XGB = GoldPricePredictorM5_XGB(pair)

#         # Get predictions
#         resultH1 = predictor.predict(show_plot=False)
#         resultM5 = predictorM5.predict(show_plot=False)
#         resultXGB = predictorM5XGB.predict(show_plot=False)

#         # Safe initialization
#         metrics, current_price, next_price, predicted_change, current_time, predicted_time = resultH1 or ({}, 0, 0, 0, '', '')
#         metricsM5, current_priceM5, next_priceM5, predicted_changeM5, current_timeM5, predicted_timeM5 = resultM5 or ({}, 0, 0, 0, '', '')
#         metricsXGB, current_priceXGB, next_priceXGB, predicted_changeXGB, current_timeXGB, predicted_timeXGB = resultXGB or ({}, 0, 0, 0, '', '')

#         # Ensure numeric values
#         predicted_change = predicted_change or 0
#         predicted_changeM5 = predicted_changeM5 or 0
#         predicted_changeXGB = predicted_changeXGB or 0

#         # Extract accuracy from metrics
#         accuracy_h1 = metrics.get('r2', 0.5) if metrics else 0.5
#         accuracy_m5 = metricsM5.get('r2', 0.5) if metricsM5 else 0.5
#         accuracy_xgb = metricsXGB.get('r2', 0.5) if metricsXGB else 0.5

#         # Display combined signal
#         print(Fore.LIGHTWHITE_EX, "=== Combined Trading Signal ===", Fore.WHITE)
        
#         # Calculate weighted combined signal
#         combined_signal = (
#             predicted_change * accuracy_h1 +
#             predicted_changeM5 * accuracy_m5 +
#             predicted_changeXGB * accuracy_xgb
#         ) / (accuracy_h1 + accuracy_m5 + accuracy_xgb)

#         # Display result
#         if combined_signal > 0.5:
#             print(Fore.LIGHTGREEN_EX, "Strong Buy - All models predict increase", Fore.WHITE)
#         elif combined_signal < -0.5:
#             print(Fore.LIGHTRED_EX, "Strong Sell - All models predict decrease", Fore.WHITE)
#         elif combined_signal > 0:
#             print(Fore.LIGHTGREEN_EX, "Moderate Buy - Some models predict increase", Fore.WHITE)
#         elif combined_signal < 0:
#             print(Fore.LIGHTRED_EX, "Moderate Sell - Some models predict decrease", Fore.WHITE)
#         else:
#             print("Hold - No significant change predicted")

#         # Print output for each model
#         text = f" {pair}\n 1-Hour Model: {predicted_change:+.2f} USD (Accuracy: {accuracy_h1:.2%})\n"
#         text += f" 5-Minute Model: {predicted_changeM5:+.2f} USD (Accuracy: {accuracy_m5:.2%}) \n"
#         text += f" XGBoost Model: {predicted_changeXGB:+.2f} USD (Accuracy: {accuracy_xgb:.2%}) \n"
#         text += f" Combined Signal: {combined_signal:+.2f} USD \n*******************"
#         send_to_window(text)

#         return predicted_change,current_price, next_price, predicted_time ,predicted_changeM5,current_priceM5, next_priceM5, predicted_timeM5 , predicted_changeXGB  ,current_priceXGB, next_priceXGB, predicted_timeXGB

#     except Exception as e:
#         print(f"Error getting signals: {str(e)}")
#         return 0, 0, 0
##################################################################################################

def get_signal_from_model(pair):
    """
    Get prediction signals from four different models and combine them (includes LSTM)
    """
    try:
        # Create predictor instances
        predictor = GoldPricePredictor(pair, days=30)
        predictorM5 = GoldPricePredictorM5(pair, days=7)
        predictorM5XGB = GoldPricePredictorM5_XGB(pair)
        predictorLSTM = GoldPricePredictorLSTM(pair) #, timeframe=MT5.TIMEFRAME_M15) #), days=3)

        # Get predictions
        resultH1 = predictor.predict(show_plot=False)
        resultM5 = predictorM5.predict(show_plot=False)
        resultXGB = predictorM5XGB.predict(show_plot=False)

        # Run LSTM model (returns predicted price only)
        df_lstm = predictorLSTM.fetch_data()
        current_price_lstm = df_lstm['Close'].iloc[-1]
        predictorLSTM.build_model()
        X_lstm, y_lstm = predictorLSTM.prepare_data(df_lstm)
        predictorLSTM.train(X_lstm, y_lstm, epochs=5, batch_size=32)
        predicted_price_lstm = predictorLSTM.predict_next(df_lstm)
        predicted_change_lstm = predicted_price_lstm - current_price_lstm
        accuracy_lstm = 0.5  # فرضی، تا وقتی معیاری برای ارزیابی نداریم

        # Safe unpacking
        metrics, current_price, next_price, predicted_change, current_time, predicted_time = resultH1 or ({}, 0, 0, 0, '', '')
        metricsM5, current_priceM5, next_priceM5, predicted_changeM5, current_timeM5, predicted_timeM5 = resultM5 or ({}, 0, 0, 0, '', '')
        metricsXGB, current_priceXGB, next_priceXGB, predicted_changeXGB, current_timeXGB, predicted_timeXGB = resultXGB or ({}, 0, 0, 0, '', '')

        # Ensure numeric
        predicted_change = predicted_change or 0
        predicted_changeM5 = predicted_changeM5 or 0
        predicted_changeXGB = predicted_changeXGB or 0
        predicted_change_lstm = predicted_change_lstm or 0

        # Accuracy
        accuracy_h1 = metrics.get('r2', 0.5)
        accuracy_m5 = metricsM5.get('r2', 0.5)
        accuracy_xgb = metricsXGB.get('r2', 0.5)

        # Combined signal (with LSTM included)
        combined_signal = (
            predicted_change * accuracy_h1 +
            predicted_changeM5 * accuracy_m5 +
            predicted_changeXGB * accuracy_xgb +
            predicted_change_lstm * accuracy_lstm
        ) / (accuracy_h1 + accuracy_m5 + accuracy_xgb + accuracy_lstm)

        # Print combined interpretation
        print(Fore.LIGHTWHITE_EX, "=== Combined Trading Signal ===", Fore.WHITE)
        if combined_signal > 0.5:
            print(Fore.LIGHTGREEN_EX, "Strong Buy - All models predict increase", Fore.WHITE)
        elif combined_signal < -0.5:
            print(Fore.LIGHTRED_EX, "Strong Sell - All models predict decrease", Fore.WHITE)
        elif combined_signal > 0:
            print(Fore.LIGHTGREEN_EX, "Moderate Buy - Some models predict increase", Fore.WHITE)
        elif combined_signal < 0:
            print(Fore.LIGHTRED_EX, "Moderate Sell - Some models predict decrease", Fore.WHITE)
        else:
            print("Hold - No significant change predicted")

        # Print model outputs
        text = f" {pair}\n 1-Hour Model: {predicted_change:+.2f} USD (Accuracy: {accuracy_h1:.2%})\n"
        text += f" 5-Minute Model: {predicted_changeM5:+.2f} USD (Accuracy: {accuracy_m5:.2%}) \n"
        text += f" XGBoost Model: {predicted_changeXGB:+.2f} USD (Accuracy: {accuracy_xgb:.2%}) \n"
        text += f" LSTM Model: {predicted_change_lstm:+.2f} USD (Accuracy: {accuracy_lstm:.2%}) \n"
        text += f" Combined Signal: {combined_signal:+.2f} USD \n*******************"
        send_to_window(text)

        return (
            predicted_change, current_price, next_price, predicted_time,
            predicted_changeM5, current_priceM5, next_priceM5, predicted_timeM5,
            predicted_changeXGB, current_priceXGB, next_priceXGB, predicted_timeXGB,
            predicted_change_lstm, current_price_lstm, predicted_price_lstm
        )

    except Exception as e:
        print(f"Error getting signals: {str(e)}")
        return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
##################################################################################################

# def get_signal_from_model(pair, days_h1=30, days_m5=7, days_lstm=3):
#     """
#     Get prediction signals from four different models and combine them (includes LSTM)
#     """
#     try:
#         # Create predictor instances
#         predictorH1 = GoldPricePredictor(pair, days=days_h1)
#         predictorM5 = GoldPricePredictorM5(pair, days=days_m5)
#         predictorM5XGB = GoldPricePredictorM5_XGB(pair)
#         predictorLSTM = GoldPricePredictorLSTM(symbol=pair, timeframe=mt5.TIMEFRAME_M15, days=days_lstm)

#         # Get predictions
#         resultH1 = predictorH1.predict(show_plot=False)
#         resultM5 = predictorM5.predict(show_plot=False)
#         resultXGB = predictorM5XGB.predict(show_plot=False)

#         # Run LSTM model (returns predicted price only)
#         df_lstm = predictorLSTM.fetch_data()
#         current_price_lstm = df_lstm['Close'].iloc[-1]
#         predictorLSTM.build_model()
#         X_lstm, y_lstm = predictorLSTM.prepare_data(df_lstm)
#         predictorLSTM.train(X_lstm, y_lstm, epochs=5, batch_size=32)
#         predicted_price_lstm = predictorLSTM.predict_next(df_lstm)
#         predicted_change_lstm = predicted_price_lstm - current_price_lstm
#         accuracy_lstm = 0.5  # فرضی، تا وقتی معیاری برای ارزیابی نداریم

#         # Safe unpacking
#         metrics, current_price, next_price, predicted_change, current_time, predicted_time = resultH1 or ({}, 0, 0, 0, '', '')
#         metricsM5, current_priceM5, next_priceM5, predicted_changeM5, current_timeM5, predicted_timeM5 = resultM5 or ({}, 0, 0, 0, '', '')
#         metricsXGB, current_priceXGB, next_priceXGB, predicted_changeXGB, current_timeXGB, predicted_timeXGB = resultXGB or ({}, 0, 0, 0, '', '')

#         # Ensure numeric
#         predicted_change = predicted_change or 0
#         predicted_changeM5 = predicted_changeM5 or 0
#         predicted_changeXGB = predicted_changeXGB or 0
#         predicted_change_lstm = predicted_change_lstm or 0

#         # Accuracy
#         accuracy_h1 = metrics.get('r2', 0.5)
#         accuracy_m5 = metricsM5.get('r2', 0.5)
#         accuracy_xgb = metricsXGB.get('r2', 0.5)

#         # Combined signal (with LSTM included)
#         combined_signal = (
#             predicted_change * accuracy_h1 +
#             predicted_changeM5 * accuracy_m5 +
#             predicted_changeXGB * accuracy_xgb +
#             predicted_change_lstm * accuracy_lstm
#         ) / (accuracy_h1 + accuracy_m5 + accuracy_xgb + accuracy_lstm)

#         # Print combined interpretation
#         print(Fore.LIGHTWHITE_EX, "=== Combined Trading Signal ===", Fore.WHITE)
#         if combined_signal > 0.5:
#             print(Fore.LIGHTGREEN_EX, "Strong Buy - All models predict increase", Fore.WHITE)
#         elif combined_signal < -0.5:
#             print(Fore.LIGHTRED_EX, "Strong Sell - All models predict decrease", Fore.WHITE)
#         elif combined_signal > 0:
#             print(Fore.LIGHTGREEN_EX, "Moderate Buy - Some models predict increase", Fore.WHITE)
#         elif combined_signal < 0:
#             print(Fore.LIGHTRED_EX, "Moderate Sell - Some models predict decrease", Fore.WHITE)
#         else:
#             print("Hold - No significant change predicted")

#         # Print model outputs
#         text = f" {pair}\n 1-Hour Model: {predicted_change:+.2f} USD (Accuracy: {accuracy_h1:.2%})\n"
#         text += f" 5-Minute Model: {predicted_changeM5:+.2f} USD (Accuracy: {accuracy_m5:.2%}) \n"
#         text += f" XGBoost Model: {predicted_changeXGB:+.2f} USD (Accuracy: {accuracy_xgb:.2%}) \n"
#         text += f" LSTM Model: {predicted_change_lstm:+.2f} USD (Accuracy: {accuracy_lstm:.2%}) \n"
#         text += f" Combined Signal: {combined_signal:+.2f} USD \n*******************"
#         send_to_window(text)

#         return (
#             predicted_change, current_price, next_price, predicted_time,
#             predicted_changeM5, current_priceM5, next_priceM5, predicted_timeM5,
#             predicted_changeXGB, current_priceXGB, next_priceXGB, predicted_timeXGB,
#             predicted_change_lstm, current_price_lstm, predicted_price_lstm
#         )

#     except Exception as e:
#         print(f"Error getting signals: {str(e)}")
#         return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0


##################################################################################################
## پیدا کردن لگ 
def build_and_send_analysis_text(pos,PairName, pair, ask_price, trend, final_confidence,
                                 predicted_changeM5, predicted_change, predicted_changeXGB,
                                 Baseroof, Basefloor, FrameRatesM5):
    text = ' '
    text = f"{PairName}\n"
    text += f"{pair} Price is ({ask_price} $)\n"

    if pos == 'Buy' : 
       text += f"M5️⃣ لگ صعودی و رنج# ... 🟢🟢 \n\n"
    elif pos == 'Sell' : 
       text += f"M5️⃣ لگ نزولی و رنج# ... 🔴🔴\n\n"
    # Optional/commented out sections:
    # text += f"تعداد کندل: {count}\n"
    # text += f"ارتفاع لگ: {round(high_low_diff, 2) / 10} pip\n"
    # text += f"ارتفاع رنج: {range_height} pip \n"
    # text += f"نسبت رنج به لگ: {round(range_height / high_low_diff * 1000,1) } % \n"

    text += f"سقف رنج: {Baseroof} $ \n"
    text += f"کف رنج : {Basefloor} $ \n\n"
    
    # text += f"حجم کل مجاز : {allowed_volume} Lot \n"
    # text += f"زمان کندل: {current_datetime.hour}:{current_datetime.minute} \n"

    if trend == 1:
        text += "🔘 پایش قدرت : قدرت خریدار "
    elif trend == -1:
        text += "🔘 پایش قدرت :قدرت فروشنده "
    elif trend == 0:
        text += "🔘 پایش قدرت : قدرت ها برابر "

    if final_confidence < 65:
        text += f"\n🔘 ضریب اطمینان پایش مناسب نیست ⚠️({round(final_confidence , 2)}) "
    else:
        text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "

    # text += " \n\n🔘 آنالیز LR: \n"
    # if predicted_changeM5 >= 0:
    #     text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5,1)} $\n"
    # else:
    #     text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5,1)} $\n"

    # if predicted_change >= 0:
    #     text += f"رشد بلند مدت :🔺+{round(predicted_change,1)} $\n"
    # else:
    #     text += f"رشد بلند مدت :🔻{round(predicted_change,1)} $"

    # text += f" \n🔘 آنالیز XGB: \nرشدکوتاه مدت {round(predicted_changeXGB,2)} $"

    # ارسال پیام به تلگرام و رسم نمودار
    plot_candles_and_send_telegram(FrameRatesM5, pair, text)
    text += f"\n\n* * * * * * * * * * * * * * \n"                  
    send_to_window(text)

##################################################################################################
## خروج قیمت از رنج
def build_position_text(pos,PairName, pair, close_price, trend_C, trend, final_confidence,
                            predicted_changeM5, predicted_change, predicted_changeXGB,
                            Baseroof, Basefloor, HS_Down, HS_Up, FrameRatesM5):
    text = ' '
    if pos == 'Buy' : 
       text = f"\n({PairName}) \n⬆️ Buy Position in {pair} \n"
       text += f"price: {close_price}$ \n🔺Upper Roof {Baseroof}$ \n\n"   
    elif pos == 'Sell' : 
        Text = f"\n({PairName}) \n⬇️ Sell Position in {pair} \n"
        Text += f"🔘price:{close_price}$ \n🔻Under floor {Basefloor}$ \n\n"
    if trend_C == +1:
      if pos == 'Buy' : 
        text += "🔘خروج  از سقف:  کندل قدرتمند 🐮 \n"
        if HS_Down == 1:
            text += "🔘 الگوی سر وشانه نزولی \n"
        elif HS_Up == 1:
            text += "🔘 الگوی سر وشانه صعودی \n"
      elif  pos == 'Sell' : 
        Text += f"🔘 خروج از کف: باکندل قدرتمند 🐻 \n"
        if PublicVarible.HS_Down == 1 : 
           Text += f"🔘الگوی سر وشانه نزولی \n"
        elif PublicVarible.HS_Up == 1 : 
           Text += f"🔘 الگوی سر وشانه صعودی \n"
    elif trend_C == +2:
      if  pos == 'Buy' : 
        text += "🔘 خروج از سقف:  کندل قدرتمند 🐮 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
        if HS_Down == 1:
            text += "🔘 الگوی سر وشانه نزولی \n"
        elif HS_Up == 1:
            text += "🔘 الگوی سر وشانه صعودی \n"
        PublicVarible.Baseroof = PublicVarible.Basefloor = 0
      elif   pos == 'Sell' :  
         Text +=  f"🔘خروج از کف: باکندل معولی 🐻 \n🔘حذف مقادیر سقف و کف ⚠️\n"
         if PublicVarible.HS_Down == 1 : 
            Text += f"🔘 الگوی سر وشانه نزولی \n"
         elif PublicVarible.HS_Up == 1 : 
            Text += f"🔘 الگوی سر وشانه صعودی \n"
            PublicVarible.Baseroof = PublicVarible.Basefloor = 0          
    elif trend_C == 0:
        text += "🔘 قدرت کندل ها : شناسایی نشد  🏓 \n🔘 حذف مقادیر سقف و کف ⚠️\n"
        PublicVarible.Baseroof = PublicVarible.Basefloor = 0
    elif trend_C == -1 or trend_C == -2:
        text += "🔘 وضعیت خروج : نامناسب  \n🔘 حذف مقادیر سقف و کف ⚠️\n"
        PublicVarible.Baseroof = PublicVarible.Basefloor = 0
    # تحلیل قدرت بازار
    if trend == 1:
        text += "🔘 پایش قدرت : قدرت خریدار "
    elif trend == -1:
        text += "🔘 پایش قدرت :قدرت فروشنده "
    elif trend == 0:
        text += "🔘 پایش قدرت : قدرت ها برابر "
    # ضریب اطمینان
    if final_confidence < 65:
        text += f"\n🔘 ضریب اطمینان پایش مناسب نیست ⚠️({round(final_confidence , 2)}) "
    else:
        text += f"\n✅ ضریب اطمینان پایش مناسب است ({round(final_confidence , 2)}) "
    # تصمیم نهایی
    if pos == "Buy" : 
      if trend == 1 and trend_C == 1 and final_confidence > 65 :
        text += "\n✅ موقعیت Buy: مناسب "
      else:
        text += "\n❌ موقعیت Buy: نامناسب "
    elif pos == "Sell" : 
      if trend == -1 and trend_C == -1 and final_confidence > 65 : 
        Text += f"\n✅ موقعیت Sell: مناسب "
      else : 
        Text += f"\n❌ موقعیت Sell: نامناسب "

    # # تحلیل‌های پیش‌بینی
    # text += " \n\n🔘 آنالیز LR: \n"
    # if predicted_changeM5 >= 0:
    #     text += f"رشد کوتاه مدت :🔺+{round(predicted_changeM5, 1)} $\n"
    # else:
    #     text += f"رشد کوتاه مدت :🔻{round(predicted_changeM5, 1)} $\n"

    # if predicted_change >= 0:
    #     text += f"رشد بلند مدت :🔺+{round(predicted_change, 1)} $\n"
    # else:
    #     text += f"رشد بلند مدت :🔻{round(predicted_change, 1)} $"

    # text += f" \n🔘 آنالیز XGB: \nرشدکوتاه مدت {round(predicted_changeXGB, 2)} $"

    # ارسال پیام
    plot_candles_and_send_telegram(FrameRatesM5, pair, text)
    text += f"\n\n* * * * * * * * * * * * * * \n"                  
    send_to_window(text)

    
########################################################################################

def predicted_Write(Pair ,text ):
    file_path = 'C:/ predicted.txt'  # مسیر فایل
    with open(file_path, 'a') as file:
        file.write("{}, {}\n".format(Pair, text))
       
########################################################################################
