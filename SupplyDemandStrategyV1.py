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

class MachineLearning():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M5
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
##############################################################################################################################################################
      def Main(self):
          print (Fore.LIGHTCYAN_EX,Back.BLACK ,"--------------", self.Pair,Back.RESET,Fore.RESET,"------------------ Strategy V9 M5 XAUUSDb ")
         
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None :
             
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 2500)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty: 
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
         
          if True :   

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
                                 
                                 if  SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.90 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status") 
                                 elif SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.75 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = abs(abs(entry_price - take_profit) * 0.25 + entry_price) #(entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit=take_profit, NewStopLoss=new_stop_loss, Deviation=0)
                                     print(" Buy Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.ask >= abs(abs(entry_price - take_profit) * 0.65 + entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = entry_price
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
                                 if SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.90 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = (entry_price + take_profit) / 2
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.75 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = abs(abs(entry_price - take_profit) * 0.25 - entry_price)
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 elif SymbolInfo.bid <= abs(abs(entry_price - take_profit) * 0.65 - entry_price):
                                     # محاسبه مقدار جدید برای حد ضرر (stop_loss)
                                     new_stop_loss = entry_price
                                     # اعمال تغییرات
                                     ModifyTPSLPosition(position_data, NewTakeProfit = take_profit, NewStopLoss= new_stop_loss, Deviation=0)
                                     print(" Sell Position Tp and Sl Modified to Bearish Status")
                                 else:
                                     print(f" Condition not met for ticket                             {ticket}" , "\n")

########################################################################################### دریافت اطلاعات تایم فریم ها و محاسبه اندیکاتور #########################################################################################################
         
          # ایجاد یک نمونه از کلاس
          predictor = GoldPricePredictor(self.Pair , days=30)  # دریافت داده‌های 30 روز گذشته
          predictorM5= GoldPricePredictorM5(self.Pair ,days=7)  # دریافت داده‌های 7 روز گذشته با بازه 5 دقیقه‌ای
          #predictorM5 = GoldPricePredictorM5(FrameRateM5=FrameRatesM5) 

          # دریافت پیش‌بینی‌ها
          metrics, current_price, next_price, predicted_change, current_time, predicted_time = predictor.predict(show_plot=False)
          metricsM5, current_priceM5, next_priceM5, predicted_changeM5, current_timeM5, predicted_timeM5 = predictorM5.predict(show_plot=False)
          # بررسی نتایج
          if metrics and current_price and next_price and predicted_change:
         #    print("\n=== Hourly Model Results ===")
         #    print(f"Start Date: {predictor.data_start}")
         #    print(f"End Date: {predictor.data_end}")
         #    print(f"Current Time: {current_time}")
         #    print(f"Prediction Time (1 hour ahead): {predicted_time}")
         #    print(f"Model Accuracy (R²): {metrics['r2']:.4f}")
         #    print(f"Current Gold Price: ${current_price:.2f}")
         #    print(f"Predicted Price (1 hour ahead): ${next_price:.2f}")
         #    print(f"Predicted Change: ${predicted_change:.2f}")

         #  # بررسی نتایج مدل 5 دقیقه‌ای
         #  if metricsM5 and current_priceM5 and next_priceM5 and predicted_changeM5:
         #    print("\n=== 5-Minute Model Results ===")
         #    print(f"Start Date: {predictorM5.data_start}")
         #    print(f"End Date: {predictorM5.data_end}")
         #    print(f"Current Time: {current_timeM5}")
         #    print(f"Prediction Time (30 min ahead): {predicted_timeM5}")
         #    print(f"Model Accuracy (R²): {metricsM5['r2']:.4f}")
         #    print(f"Current Gold Price: ${current_priceM5:.2f}")
         #    print(f"Predicted Price (30 min ahead): ${next_priceM5:.2f}")
         #    print(f"Predicted Change: ${predicted_changeM5:.2f}")
            
         #    # نمایش معیارهای اطمینان مدل 5 دقیقه‌ای
         #    print("\n5-Minute Model Confidence Metrics:")
         #    print(f"Success Rate (0.1%): {predictorM5.confidence_metrics['success_rate_0.1']:.2f}%")
         #    print(f"Directional Accuracy: {predictorM5.confidence_metrics['directional_accuracy']:.2f}%")
         #    print(f"Trend Accuracy: {predictorM5.confidence_metrics['trend_accuracy']:.2f}%")
            
         #    # محاسبه و نمایش سطح اطمینان کلی مدل 5 دقیقه‌ای
         #    confidence_score = (
         #        predictorM5.confidence_metrics['success_rate_0.1'] * 0.4 +
         #        predictorM5.confidence_metrics['directional_accuracy'] * 0.3 +
         #        predictorM5.confidence_metrics['trend_accuracy'] * 0.3
         #    )
         #    print(f"Overall Prediction Confidence: {confidence_score:.2f}%")
            
            # نمایش سیگنال معاملاتی ترکیبی
            print("\n=== Combined Trading Signal ===")
            if predicted_change > 0 and predicted_changeM5 > 0:
                print("STRONG BUY - Both models predict increase")
                print(f"Hourly Model: +${predicted_change:.2f}")
                print(f"5-Minute Model: +${predicted_changeM5:.2f}")
            elif predicted_change < 0 and predicted_changeM5 < 0:
                print("STRONG SELL - Both models predict decrease")
                print(f"Hourly Model: -${abs(predicted_change):.2f}")
                print(f"5-Minute Model: -${abs(predicted_changeM5):.2f}")
            elif predicted_change > 0 or predicted_changeM5 > 0:
                print("MODERATE BUY - One model predicts increase")
                print(f"Hourly Model: ${predicted_change:.2f}")
                print(f"5-Minute Model: ${predicted_changeM5:.2f}")
            elif predicted_change < 0 or predicted_changeM5 < 0:
                print("MODERATE SELL - One model predicts decrease")
                print(f"Hourly Model: ${predicted_change:.2f}")
                print(f"5-Minute Model: ${predicted_changeM5:.2f}")
            else:
                print("HOLD - No significant change expected")
