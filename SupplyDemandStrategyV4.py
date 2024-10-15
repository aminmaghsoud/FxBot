import pandas as PD
from Utility import *
from Trade import *
import MetaTrader5 as MT5
from colorama import init, Fore, Back, Style
from datetime import datetime
import PublicVarible
import pandas_ta as PTA


class SupplyDemandStrategyV4():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
           
##############################################################################################################################################################
      def Main(self):
          SymbolInfo = MT5.symbol_info(self.Pair)
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ StrategyV4 M1 Spike --------------")
          if self.Pair != 'XAUUSDb' : 
              return
          buy_positions_with_open_prices = get_buy_positions_with_open_prices()
          if buy_positions_with_open_prices:
                      for ticket, open_price in buy_positions_with_open_prices.items():
                          position_data = {
                              "symbol": self.Pair,  # نماد
                              "ticket": ticket,     # شماره تیکت موقعیت
                          }
                          positions = MT5.positions_get()
                          for position_info in positions:
                             if position_info.ticket == ticket and position_info.symbol == self.Pair :
                                 entry_price = position_info.price_open
                                 take_profit = position_info.tp
                                 stoploss = position_info.sl
                                 if SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.7 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

          sell_positions_with_open_prices = get_sell_positions_with_open_prices()
          if sell_positions_with_open_prices:
                      for ticket, open_price in sell_positions_with_open_prices.items():
                          position_data = {
                              "symbol": self.Pair,  # نماد
                              "ticket": ticket,     # شماره تیکت موقعیت
                          }
                          positions = MT5.positions_get()
                          for position_info in positions:
                             if position_info.ticket == ticket and position_info.symbol == self.Pair :
                                 entry_price = position_info.price_open
                                 take_profit = position_info.tp
                                 stoploss = position_info.sl
                                 if SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.7 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

         
          if SymbolInfo is not None :
            RatesM1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M1, 0, 250)
            if RatesM1 is not None:
                FrameRatesM1 = PD.DataFrame(RatesM1)
                if not FrameRatesM1.empty:
                   FrameRatesM1['datetime'] = PD.to_datetime(FrameRatesM1['time'], unit='s')
                   FrameRatesM1 = FrameRatesM1.drop('time', axis=1)
                   FrameRatesM1 = FrameRatesM1.set_index(PD.DatetimeIndex(FrameRatesM1['datetime']), drop=True)   
          
          current_datetime = datetime.now()
          time_difference = (current_datetime - PublicVarible.trade_datetime).total_seconds()
          print("time_difference" , time_difference)
          if time_difference < 61:
             
             Botdashboard(4 , self.Pair)
             return
   
########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
         
          swing_High = 0
          swing_Low = 0

          H2= FrameRatesM1.iloc[-2]['high']
          H3 = FrameRatesM1.iloc[-3]['high'] 
          H4 = FrameRatesM1.iloc[-4]['high'] 
          H5 = FrameRatesM1.iloc[-5]['high'] 
          L2 = FrameRatesM1.iloc[-2]['low']
          L3 = FrameRatesM1.iloc[-3]['low']
          L4 = FrameRatesM1.iloc[-4]['low']
          L5 = FrameRatesM1.iloc[-5]['low']
          C2 = FrameRatesM1.iloc[-2]['close']
             
          if H3 > H2 and H3 > H4 and  H5 < H4 and C2 < L3 : 
             swing_High = 1  
          elif L3 < L2 and L3 < L4 and L5 > L4 and C2 > H3 : 
               swing_Low = 1 
          else : return

          trade_datetime = datetime(2024, 10, 7, 12, 0, 0) 
          current_datetime = datetime.now()
          time_difference = (current_datetime - trade_datetime).total_seconds()
          print("time_difference " , time_difference )
          if time_difference < 61:
             Botdashboard(4 , self.Pair)
             return

          if swing_High == 1 : 
                EntryPrice = SymbolInfo.ask                                                                                        ######### قیمت  ورود به معامله ##########
                SL = H3 + ( SymbolInfo.point * 50)                                                                               #########  تعیین حدضرر معامله #########
                Balance = GetBalance()
                Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2) 
                TP1 = EntryPrice - (abs(EntryPrice - SL) * 2 )
                PublicVarible.trade_datetime = datetime.now()
                print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment=  "V4 - M1")
            
          if swing_Low == 1 : 
                EntryPrice = SymbolInfo.ask 
                SL = L3 - ( SymbolInfo.point * 50)    #########  تعیین حدضرر معامله #########
                Balance = GetBalance()
                Volume = round((Balance * 0.02) / (abs(SL - EntryPrice) / SymbolInfo.point) , 2)   
                TP1 = (abs(EntryPrice - SL) * 2 ) + EntryPrice  #SymbolInfo.bid + ( SymbolInfo.point * 100)  
                PublicVarible.trade_datetime = datetime.now()
                print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= "V4 - M1")


########################################################################################################
def CalcLotSize():
    balance = GetBalance()
    return math.sqrt(balance) / 500