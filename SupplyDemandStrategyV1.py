import pandas_ta as PTA
import pandas as PD
from colorama import Fore, Style
import MetaTrader5 as MT5
import PublicVarible

class SupplyDemandStrategyV1():
    Pair = ""
    TimeFrame = MT5.TIMEFRAME_M15

    def __init__(self, Pair):
        self.Pair = Pair

    def Main(self):
        print(Fore.LIGHTCYAN_EX, "--------------", self.Pair, "------------------ StrategyV1 Swing ...  --------------", Fore.RESET)
        if self.Pair != 'XAUUSDb': 
            return

        SymbolInfo = MT5.symbol_info(self.Pair)
        if SymbolInfo is not None:
            RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
            if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                    FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                    FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                    FrameRatesM5 = FrameRatesM5.set_index('datetime')

                    # محاسبه HMA و حذف مقدارهای NaN
                    FrameRatesM5["HMA_150"] = PTA.hma(FrameRatesM5['close'], length=150).dropna()
                    FrameRatesM5["HMA_50"] = PTA.hma(FrameRatesM5['close'], length=50).dropna()

                    if len(FrameRatesM5) < 2:  # جلوگیری از خطا در diff()
                        return

                    # مقدار آخر و مقدار قبلی برای مقایسه
                    last_row = FrameRatesM5.iloc[-1]
                    prev_hma_150 = FrameRatesM5["HMA_150"].iloc[-2]
                    prev_hma_50 = FrameRatesM5["HMA_50"].iloc[-2]

                    # اجرای تابع و ذخیره مقدار خروجی
                    hma_info = get_hma_info(last_row, prev_hma_150, prev_hma_50)

                    # محاسبه مقدار hmaSignal
                    PublicVarible.hmaSignal = get_hma_signal(hma_info)

                    # نمایش خروجی در ترمینال
                    print_hma_output(hma_info, PublicVarible.hmaSignal)
                    

# **تابعی که مقدار HMA و رنگ آن را برمی‌گرداند**
def get_hma_info(last_row, prev_hma_150, prev_hma_50):
    hma_150_up = last_row["HMA_150"] > prev_hma_150
    hma_50_up = last_row["HMA_50"] > prev_hma_50

    return {
        "HMA_150": {
            "value": last_row["HMA_150"],
            "color": Fore.GREEN if hma_150_up else Fore.RED,
            "trend": "صعودی" if hma_150_up else "نزولی"
        },
        "HMA_50": {
            "value": last_row["HMA_50"],
            "color": Fore.GREEN if hma_50_up else Fore.RED,
            "trend": "صعودی" if hma_50_up else "نزولی"
        }
    }

# **تابعی که مقدار hmaSignal را تعیین می‌کند**
def get_hma_signal(hma_info):
    hma_150_color = hma_info["HMA_150"]["color"]
    hma_50_color = hma_info["HMA_50"]["color"]

    if hma_150_color == Fore.GREEN and hma_50_color == Fore.GREEN:
        return 1  # هر دو صعودی (سبز)
    elif hma_150_color == Fore.RED and hma_50_color == Fore.RED:
        return -1  # هر دو نزولی (قرمز)
    else:
        return 0  # یکی صعودی و دیگری نزولی

# **تابعی که مقدار را در ترمینال نمایش می‌دهد**
def print_hma_output(hma_info, hmaSignal):
    print(f"HMA_150: {hma_info['HMA_150']['color']}{hma_info['HMA_150']['value']:.2f} ({hma_info['HMA_150']['trend']}){Style.RESET_ALL}")
    print(f"HMA_50: {hma_info['HMA_50']['color']}{hma_info['HMA_50']['value']:.2f} ({hma_info['HMA_50']['trend']}){Style.RESET_ALL}")
    print(f"hmaSignal: {hmaSignal} ")

