import pandas as PD
from Utility import *
from Trade import *
import time
from datetime import datetime
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
import PublicVarible
from GoldPricePredictor import *
from GoldPricePredictorM5 import *
from GoldPricePredictorM5_XGB import GoldPricePredictorM5_XGB

class SupplyDemandStrategyV10():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          PairNameX = self.Pair #"دلار امریکا/ اونس طلا"
          if self.Pair != "XAUUSDb" : return
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V10 M5 XAUUSDb ")

          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             
             RatesM15 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M15, 0, 100)
             if RatesM15 is not None:
                FrameRatesM15 = PD.DataFrame(RatesM15)
                if not FrameRatesM15.empty: 
                   FrameRatesM15['datetime'] = PD.to_datetime(FrameRatesM15['time'], unit='s')
                   FrameRatesM15 = FrameRatesM15.drop('time', axis=1)
                   FrameRatesM15 = FrameRatesM15.set_index(PD.DatetimeIndex(FrameRatesM15['datetime']), drop=True)

             RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 100)
             if RatesM30 is not None:
                FrameRatesM30 = PD.DataFrame(RatesM30)
                if not FrameRatesM30.empty: 
                   FrameRatesM30['datetime'] = PD.to_datetime(FrameRatesM30['time'], unit='s')
                   FrameRatesM30 = FrameRatesM30.drop('time', axis=1)
                   FrameRatesM30 = FrameRatesM30.set_index(PD.DatetimeIndex(FrameRatesM30['datetime']), drop=True)

             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 100)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
          
          ATR = PTA.atr(high = FrameRatesM5['high'],low = FrameRatesM5['low'], close = FrameRatesM5['close'],length=14)
          ATR_Value = ATR.iloc[-1]
          Atr_Tp = (ATR_Value / SymbolInfo.point) *0.8
          print("ATR_pip :" , Atr_Tp)

          Stoch = PTA.stochrsi(close = FrameRatesM5['close'],length=5,rsi_length=14)
          k_stoch = Stoch.iloc[-1][-2] #جدیدترین مقدار k
          d_stoch = Stoch.iloc[-1][-1] #جدیدترین مقدار d
          (
           predicted_change, current_price, next_price, predicted_time,
           predicted_changeM5, current_priceM5, next_priceM5, predicted_timeM5,
           predicted_changeXGB, current_priceXGB, next_priceXGB, predicted_timeXGB,
           predicted_changeLSTM, current_priceLSTM, predicted_priceLSTM
          ) = get_signal_from_model(self.Pair)

         # predicted_change,current_price, next_price, predicted_time ,predicted_changeM5,current_priceM5, next_priceM5, predicted_timeM5 , predicted_changeXGB  ,current_priceXGB, next_priceXGB, predicted_timeXGB = get_signal_from_model(self.Pair)
                    
          if True :   
             trend5 ,  final_confidence = analyze_market_power(FrameRatesM5, FrameRatesM15, FrameRatesM30) 
             print(" trend5: ",trend5 , "final_confidence: " ,round(final_confidence,2) )
             text = f"{predicted_change},{predicted_changeM5},{predicted_changeXGB},{trend5},{final_confidence},{k_stoch},{d_stoch},{datetime.now()}"
             predicted_Write(self.Pair ,text )
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             # دریافت زمان فعلی
             current_time = time.time()
             current_datetime = datetime.now()
             # تعریف بازه‌های زمانی ممنوعه
             restricted_time_ranges = [
                (0, 0, 2, 30),   
                (8, 0, 9, 0),  
                (15, 45, 19, 00),  
                (23, 0, 23, 59)   # 22:00 تا 23:59
             ]
             # بررسی اینکه آیا ساعت جاری در یکی از بازه‌های ممنوعه است یا خیر
             in_restricted_time = any(
                start_h * 60 + start_m <= current_datetime.hour * 60 + current_datetime.minute <= end_h * 60 + end_m
                for start_h, start_m, end_h, end_m in restricted_time_ranges
             )

             if in_restricted_time or not PublicVarible.CanOpenOrder or not PublicVarible.Quick_trade :
                 Botdashboard(4, self.Pair)
                 Time_Signal = 0

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
             Balace = GetBalance()

             buy_positions_with_open_prices = get_buy_positions_with_open_prices()                 ######### بررسی معامله خرید باز  ##########
             if buy_positions_with_open_prices:
                 for ticket, open_price in buy_positions_with_open_prices.items():
                   positions = MT5.positions_get()
                   for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(53 , self.Pair)
                        return

             sell_positions_with_open_prices = get_sell_positions_with_open_prices()           ######### بررسی معامله فروش باز  ##########
             if sell_positions_with_open_prices:
                  for ticket, open_price in sell_positions_with_open_prices.items():
                    positions = MT5.positions_get()
                    for position_info in positions:
                     if position_info.symbol == self.Pair :
                        Botdashboard(54 , self.Pair)
                        return
             
#########################  بررسی قدرت کندل خروج    #########################    
             trend_C = 0
             close_C = FrameRatesM15.iloc[-2]['close']
             high_C = FrameRatesM15.iloc[-2]['high'] 
             low_C = FrameRatesM15.iloc[-2]['low']
             high_C_O = FrameRatesM15.iloc[-3]['high'] 
             low_C_O = FrameRatesM15.iloc[-3]['low']
             One_third_UP = high_C - ((high_C - low_C) / 3)
             One_third_Down = low_C + ((high_C - low_C) / 3)
             if  close_C >= One_third_UP and close_C > high_C_O  :
                 trend_C = +1
             elif close_C <= One_third_Down and close_C < low_C_O :
                 trend_C = -1
            
             LRM5pip = abs(predicted_changeM5) / SymbolInfo.point
             LRXGBpip = abs(predicted_changeXGB) / SymbolInfo.point
             print(f"LRM5pip: {LRM5pip} point \nLRXGBpip: {LRXGBpip} point")

#Buy####################  بررسی شرط معامله خرید ######################
             
             if predicted_change > 0 and  predicted_changeM5 > 0 and LRM5pip > 10 and predicted_changeXGB > 0  and LRXGBpip > 10 and trend_C == 1  and k_stoch < 20  :
                
                #Buy
                EntryPrice = SymbolInfo.ask
                TP1 = EntryPrice  + (SymbolInfo.point * Atr_Tp) #((predicted_changeM5 + predicted_changeXGB)/ 2)
                SL   = 0 #EntryPrice - (SymbolInfo.point * Atr_Tp)  #((predicted_changeM5 + predicted_changeXGB)/ 2)
                Entryheight = round(abs(EntryPrice - SL) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace * 0.8) * (PublicVarible.risk/1000) / Entryheight , 2)   
                if trend5 != 1 : Volume = round(Volume/2 , 2)
                OrderBuy(Pair= self.Pair, Volume= Volume  , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "Mar V10")
                
                if current_time - PublicVarible.last_execution_timeV10 >= 300:   
                  text =  f"🔖Signal {self.Pair} \n"
                  text += f"🟢Buy (یادگیری ماشین)\n"
                  text += f"🔖current_price H1:{round(current_price,3)} \n"
                  text += f"🔖predicted_time: {predicted_time}  \n"
                  #text += f"🔖predicted_changeXGB:{round(predicted_changeXGB,3)} \n"
                  #text += f"🔖LRXGBpip: {round(LRXGBpip,3)}point ,\n"
                  if trend5 == 1 : 
                     text += f"🔖trend: صعودی ({round(final_confidence,2)}) \n"
                  elif trend5 == -1 : 
                     text += f"🔖trend: نزولی ({round(final_confidence,2)}) \n"
                  else : 
                     text += f"🔖trend: بدون جهت ({round(final_confidence,2)}) \n"
                  text += f"🔖EntryPrice: {round(SymbolInfo.ask,3)}\n"
                  text += f"🔖Volume: {round(Volume,2)}\n"
                  text += f"🔖S/L: {round(SL,3)}\n🔖T/P: {round(TP1,3)}"
                  plot_candles_and_send_telegram(FrameRatesM5, self.Pair, text)   
                  PromptToTelegram(text)
                  text += f"\n\n* * * * * * * * * * * * * * \n"
                  send_to_window(text)
                  PublicVarible.last_execution_timeV10 = current_time  

                
                Prompt(f"Signal {self.Pair} Type:Buy,predicted_changeM5:{predicted_changeM5},predicted_changeXGB:{predicted_changeXGB}")


#Sell####################  بررسی شرط معامله فروش ######################

             if predicted_change < 0 and predicted_changeM5 < 0 and LRM5pip > 10 and predicted_changeXGB < 0  and LRXGBpip > 10 and trend_C == -1  and k_stoch > 80 :
                
                #Sell
                EntryPrice = SymbolInfo.bid 
                TP1 = EntryPrice -  (SymbolInfo.point * Atr_Tp) #((predicted_changeM5 + predicted_changeXGB)/ 2)
                SL   = 0 #EntryPrice + (SymbolInfo.point * Atr_Tp)  #((predicted_changeM5 + predicted_changeXGB)/ 2)
                Entryheight = round(abs(EntryPrice - SL) / (SymbolInfo.point) / 10, 2)      
                Volume = round((Balace) * (PublicVarible.risk/1000) / Entryheight , 2)
                if trend5 != -1 : Volume = round(Volume/2 , 2)
                OrderSell(Pair= self.Pair, Volume= Volume  , StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "Mar V10")

                if current_time - PublicVarible.last_execution_timeV10 >= 300:   
                  text =  f"🔖Signal {self.Pair} \n"
                  text += f"🔴Sell (یادگیری ماشین)\n"
                  text += f"🔖current_price H1:{round(current_price,3)} \n"
                  text += f"🔖predicted_time: {predicted_time}  \n"
                  #text += f"🔖predicted_changeXGB:{round(predicted_changeXGB,3)} \n"
                  #text += f"🔖LRXGBpip: {round(LRXGBpip,3)}point ,\n"
                  if trend5 == 1 : 
                     text += f"🔖trend: صعودی ({round(final_confidence,2)}) \n"
                  elif trend5 == -1 : 
                     text += f"🔖trend: نزولی ({round(final_confidence,2)}) \n"
                  else : 
                     text += f"🔖trend: بدون جهت ({round(final_confidence,2)}) \n"
                  text += f"🔖EntryPrice: {round(SymbolInfo.bid ,3)}\n"
                  text += f"🔖Volume: {round(Volume ,2)}\n"
                  text += f"🔖S/L: {round(SL,3)}\n🔖T/P: {round(TP1,3)}"
                  plot_candles_and_send_telegram(FrameRatesM5, self.Pair, text)   
                  PromptToTelegram(text)
                  text += f"\n\n* * * * * * * * * * * * * * \n"                  
                  send_to_window(text)
                  PublicVarible.last_execution_timeV10 = current_time  

                Prompt(f"Signal {self.Pair} Type:Sell,predicted_changeM5:{predicted_changeM5},predicted_changeXGB:{predicted_changeXGB}")

                                
########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500