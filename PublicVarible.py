import concurrent.futures
import pytz
from Utility import *
import time
from datetime import datetime
import tkinter as tk
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
TelegramChatId = [152284556 , 388239785 , 98785822]
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
risk = 2
current_datetime = datetime.now()
if  current_datetime.weekday() in [1 , 3  , 4]  : 
  risk = 1
elif  current_datetime.weekday() in [0 , 2]  : 
  risk = 3

Quick_trade = False
lot_size = 0.01
Quick_trade = False
CanOpenOrder = True

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
    root.geometry("500x300")

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
    tk.Label(right_frame, text=" (فعال یا غیرفعال کردن)معامله سریع", font=("B Nazanin", 12), bg=right_bg_color, fg="black").pack(anchor="e", padx=20, pady=10)
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

    tk.Button(left_frame, text="اعمال تغییرات", bg="red", fg="white", font=("B Nazanin", 12), command=save).pack(anchor="w", padx=20, pady=20)

    root.mainloop()


gui_thread = Thread(target=create_gui)
gui_thread.start()