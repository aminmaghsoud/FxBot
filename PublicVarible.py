import concurrent.futures
import pytz
from Utility import *
from datetime import datetime
import tkinter as tk
import sys
from threading import Thread
########################################################################################################
#ConnectionString = ("Driver={ODBC Driver 18 for SQL Server}; Server=.; Database=FxBotDB; UID=sa; PWD=qazwsx!@#6027; Encrypt=no;")
ConnectionString = (r"Driver={ODBC Driver 18 for SQL Server}; Server=.\FXBOT; Database=FxBotDB; UID=sa; PWD=qazwsx!@#6027; Encrypt=no;") 
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
CanOpenOrder = False
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
TelegramChatId = [152284556 , 388239785 , 98785822 , 1864188026]
chat_ids = [152284556 , 388239785 , 98785822 , 1864188026 , 92618613 , 76616815 , 6958871546 , 38776931 , 7318507893 , 85415218 , 381177412]

LastTelegramUpdateId = -1
# آخرین زمانی که ربات اعلام آماده بودن کرده است
LastDatetimeRobotIsReady = None 
Botstatus = 0

########################################################################################################
########################################### Strategy Settings ##########################################
########################################################################################################
#LossPrecent = 0
#targetProfit = 0
#TrailingTP = 0
#TrailingSL = 0
#LastStoplossChange = None
#lastclose = 0
#LastBuyPrice = 0
#LastSellPrice = 0
#MFIover = 0 
#firstBuy = 100
#firstSell = 100
#last_message_time = 0
#last_message_time1 = 0
last_execution_timeAll = 0
############# xauusd ################## VER 9
last_execution_time = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timeS = 0
last_execution_timeM15 = 0  
last_execution_timeT = 0
Basefloor5 = 0.0
Baseroof5 = 0.0
HS_Down = 0 
HS_Up = 0
range_height = 0
List_of_high = 0
List_of_low = 0
Basetime = 0
Limittime = 0 
high_low_diff = 0
prediction = 0
model = 0
Accuracy = 100
Leg_trend = 0
predicted_changeM5 = 0
predicted_change = 0
############# USDJPY ################## VER 8
last_execution_timej = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timejS = 0 
Basefloorj = 0.0
Baseroofj = 0.0
Basetimej = 0
range_heightj = 0
LowerLj = 0
HigherHj = 0
HS_DownJ = 0 
HS_UpJ = 0
Leg_startj = 0
high_low_diffj = 0
predictionj = 0
modelj = 0
Accuracyj = 0
Leg_trendj = 0
predicted_changeM5j = 0
predicted_changej = 0
############# BTCUSD ################## VER 6
last_execution_timeB = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timeBS = 0 
BasefloorB = 0.0
BaseroofB = 0.0
BasetimeB = 0
range_heightB = 0
LowerLB = 0
HigherHB = 0
HS_DownB = 0 
HS_UpB = 0
high_low_diffB = 0
predictionB = 0
modelB = 0
AccuracyB = 0
Leg_trendB = 0
predicted_changeM5B = 0
predicted_changeB = 0
############# CADJPY ################## VER 4
last_execution_timeN = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timeNS = 0 
BasefloorN = 0.0
BaseroofN = 0.0
BasetimeN = 0
range_heightN = 0
LowerLN = 0
HigherHN = 0
HS_DownN = 0 
HS_UpN = 0
Leg_startN = 0
high_low_diffN = 0
predictionN = 0
modelN = 0
AccuracyN = 0
predicted_changeM5N = 0
predicted_changeN = 0
############# EURjpy  ################## VER 7
last_execution_timeE = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timeES = 0 
BasefloorE = 0.0
BaseroofE = 0.0
BasetimeE = 0
range_heightE = 0
LowerLE = 0
HigherHE = 0
HS_DownE = 0 
HS_UpE = 0
high_low_diffE = 0
predictionE = 0
modelE = 0
AccuracyE = 0
Leg_trendE = 0
predicted_changeM5E = 0
predicted_changeE = 0
############# CHFJPY ################## VER 5
last_execution_timeU = 0  # در ابتدا 0 یا هر مقدار مناسب دیگر
last_execution_timeUS = 0 
BasefloorU = 0.0
BaseroofU = 0.0
BasetimeU = 0
range_heightU = 0
LowerLU = 0
HigherHU = 0
HS_DownU = 0 
HS_UpU = 0
high_low_diffU = 0 
predictionU = 0
modelU = 0
AccuracyU = 0
Leg_trendU = 0
predicted_changeM5U = 0
predicted_changeU = 0
############# LegAnalyzer ##################
"""BasefloorLA = 0.0
BaseroofLA = 0.0
range_heightLA = 0
LowerLLA = 0
HigherHLA = 0
HS_DownLA = 0 
HS_UpLA = 0
high_low_diffLA = 0
"""


Quick_trade = False
lot_size = 0.02
risk = 1
current_datetime = datetime.now()
if  current_datetime.weekday() in [1 , 3  , 4]  : 
  risk = 1
elif  current_datetime.weekday() in [0 , 2]  : 
  risk = 3
trade_datetime = datetime.now()




def update_variables(new_risk, new_lot_size, new_quick_trade, new_can_open_order):
    PublicVarible.risk = new_risk
    PublicVarible.lot_size = new_lot_size
    PublicVarible.Quick_trade = new_quick_trade
    PublicVarible.CanOpenOrder = new_can_open_order
    print(f"Risk updated to: {PublicVarible.risk}")
    print(f"Lot Size updated to: {PublicVarible.lot_size}")
    print(f"Quick Trade updated to: {PublicVarible.Quick_trade}")
    print(f"Can Open Order updated to: {PublicVarible.CanOpenOrder}")

def create_gui():
    root = tk.Tk()
    root.title("تنظیمات ربات")
    root.geometry("500x400")

    # رنگ پس‌زمینه
    right_bg_color = "yellow"
    left_bg_color = "gray"

    # ایجاد فریم سمت راست و چپ
    right_frame = tk.Frame(root, bg=right_bg_color, width=300, height=600)
    left_frame = tk.Frame(root, bg=left_bg_color, width=500, height=600)

    right_frame.pack_propagate(False)
    left_frame.pack_propagate(False)

    right_frame.place(x=0, y=0, width=300, height=600)
    left_frame.place(x=300, y=0, width=500, height=600)

    # رسم خط از بالا تا پایین صفحه
    canvas = tk.Canvas(root, width=2, height=600, bg="black")
    canvas.place(x=300, y=0)

    # فیلدهای سمت راست (عناوین و توضیحات)
    tk.Label(right_frame, text="(1 = Low  -- 2 = Med  --  3 = High)ریسک", font=("B Nazanin", 12), bg=right_bg_color, fg="black").pack(anchor="e", padx=20, pady=10)
    tk.Label(right_frame, text=" (حجم معاملات را تعیین کنید.)لات سایز", font=("B Nazanin", 12), bg=right_bg_color, fg="black").pack(anchor="e", padx=20, pady=10)
    tk.Label(right_frame, text=" (فعال یا غیرفعال کردن)معامله xauusd", font=("B Nazanin", 12), bg=right_bg_color, fg="black").pack(anchor="e", padx=20, pady=10)
    tk.Label(right_frame, text="اجازه به باز کردن سفارش", font=("B Nazanin", 12), bg=right_bg_color, fg="black").pack(anchor="e", padx=20, pady=10)

    # فیلدهای سمت چپ (ورودی‌ها)
    risk_entry = tk.Entry(left_frame, font=("B Nazanin", 12), bg=left_bg_color, fg="black")
    risk_entry.pack(anchor="w", padx=20, pady=10)
    risk_entry.insert(0, PublicVarible.risk)

    lot_size_entry = tk.Entry(left_frame, font=("B Nazanin", 12), bg=left_bg_color, fg="black")
    lot_size_entry.pack(anchor="w", padx=20, pady=10)
    lot_size_entry.insert(0, PublicVarible.lot_size)

    quick_trade_var = tk.BooleanVar(value=PublicVarible.Quick_trade)
    quick_trade_checkbox = tk.Checkbutton(left_frame, variable=quick_trade_var, bg=left_bg_color, fg="black", font=("B Nazanin", 12), activebackground=left_bg_color, activeforeground="white", selectcolor=left_bg_color)
    quick_trade_checkbox.pack(anchor="w", padx=20, pady=10)

    can_open_order_var = tk.BooleanVar(value=PublicVarible.CanOpenOrder)
    can_open_order_checkbox = tk.Checkbutton(left_frame, variable=can_open_order_var, bg=left_bg_color, fg="black", font=("B Nazanin", 12), activebackground=left_bg_color, activeforeground="white", selectcolor=left_bg_color)
    can_open_order_checkbox.pack(anchor="w", padx=20, pady=10)

    # دکمه ذخیره
    def save():
        try:
            new_risk = float(risk_entry.get())
            new_lot_size = float(lot_size_entry.get())
            new_quick_trade = quick_trade_var.get()
            new_can_open_order = can_open_order_var.get()
            update_variables(new_risk, new_lot_size, new_quick_trade, new_can_open_order)
        except ValueError:
            print("مقدار وارد شده معتبر نیست.")
    def close():
        root.destroy()
        sys.exit()

    tk.Button(left_frame, text="اعمال تغییرات", bg="black", fg="white", font=("B Nazanin", 12), command=save).pack(anchor="w", padx=20, pady=20)
    tk.Button(left_frame, text="خروج از برنامه", bg="red", fg="white", font=("B Nazanin", 12), command=close).pack(anchor="w", padx=20, pady=20)

    root.mainloop()


gui_thread = Thread(target=create_gui)
gui_thread.start()


