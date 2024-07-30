import concurrent.futures
import pytz
from Utility import *
import time
########################################################################################################
ConnectionString = (r"Driver={ODBC Driver 18 for SQL Server}; Server=.\FXBOT; Database=FxBotDB; UID=sa; PWD=qazwsx!@#6027; Encrypt=no;")
#ConnectionString = "Driver={ODBC Driver 18 for SQL Server}; Server=WIN-GREOR96KJAS; Database=FXBOT; Trusted_Connection=yes;"

# آی دی ربات
Id = 2 
# عنوان ربات
Name = ""
# بالانس مجازی حساب
VirtualBalance = 0
# تعداد اوردرهای باز همزمان
MaxOpenTrades = 0
# واحد نمایش پول
StakeCurrency = ""
# نام کاربری جهت اتصال به بروکر
Username = ""
# کلمه عبور
Password = ""
# سرور
Server = ""
# تایم اوت زمانی
Timeout = 0
# فهرست جفت ارزها
Pair = [] 
# ضریب افزایش لات سایز بر حسب دلار بالانس
LotIncreaseRatio = 0
TradesStartTime = "00:00"
TradesEndTime = "00:00"
StopTradesBeforeNews = 0
StopTradesAfterNews = 0
# فهرست اخبار
News = []
# آیا مارکت باز است
MarketIsOpen = False
# آیا ربات فعال است
StartBot = True
# آیا ربات میتواند سفارشی باز کند
CanOpenOrder = True
CanOpenOrderST = True
# تاریخ ایجاد ربات
CreateAt = None
# تاریخ انقضاء ربات
ExpireAt = None
# فهرست لاگ های ربات
LstLog = []
# ساعت محلی به وقت بروکر
BrokerTimeZone = pytz.timezone("Asia/Istanbul")  #Etc/GMT-3
Executor = concurrent.futures.ThreadPoolExecutor()
TelegramToken = ""
TelegramBot = None
TelegramChatId = [177496720, 388239785,5386526087,294153466]
LastTelegramUpdateId = -1
# آخرین زمانی که ربات اعلام آماده بودن کرده است
LastDatetimeRobotIsReady = None
########################################################################################################
########################################### Strategy Settings ##########################################
########################################################################################################
LossPrecent = 0
targetProfit = 0
TrailingTP = 0
TrailingSL = 0
LastStoplossChange = None
lastclose = 0
Botstatus = 0
LastBuyPrice = 0
LastSellPrice = 0
MFIover = 0 
firstBuy = 100
firstSell = 100
last_message_time = time.time()
last_message_time1 = time.time()