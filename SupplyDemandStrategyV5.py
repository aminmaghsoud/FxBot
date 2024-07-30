from math import floor
from xmlrpc.client import DateTime
from matplotlib.colors import Normalize
import pandas_ta as PTA
import pandas as PD
from scipy.signal import normalize
from Utility import *
from Trade import *
import PublicVarible
from ZigzagIndicator2 import *
import MetaTrader5 as MT5


class SupplyDemandStrategyV5():
      Pair = ""
      TimeFrame = MT5.TIMEFRAME_M1
########################################################################################################
      def __init__(self, Pair):
          self.Pair = Pair
          
########################################################################################################
      def Main(self):
          SymbolInfo = MT5.symbol_info(self.Pair)
          if SymbolInfo is not None:
             RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 250)
             if RatesM5 is not None:
                FrameRatesM5 = PD.DataFrame(RatesM5)
                if not FrameRatesM5.empty:
                   FrameRatesM5['datetime'] = PD.to_datetime(FrameRatesM5['time'], unit='s')
                   FrameRatesM5 = FrameRatesM5.drop('time', axis=1)
                   FrameRatesM5 = FrameRatesM5.set_index(PD.DatetimeIndex(FrameRatesM5['datetime']), drop=True)
                   ADX = PTA.trend.adx(high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 15)                         #ADX calculation
                   if ADX.iloc[-1][0] > 19.5  and ADX.iloc[-1][0] < 22.5 :                                                                                 # Market is on border
                      print("ADX: ", round(ADX.iloc[-1][0], 1)," the Market is on border ...")
                   elif ADX.iloc[-1][0] <= 19.5 :  
                      print("ADX: ", round(ADX.iloc[-1][0], 1)," Market no Direction ...")
                   elif ADX.iloc[-1][0] > 22.5 :  
                      print("ADX: ", round(ADX.iloc[-1][0], 1)," Market is Directional ...")
                   
                   RatesM1 = MT5.copy_rates_from_pos(self.Pair, self.TimeFrame, 0, 260)
                   if RatesM1 is not None:
                      FrameRatesM1 = PD.DataFrame(RatesM1)
                      if not FrameRatesM1.empty:
                         FrameRatesM1['datetime'] = PD.to_datetime(FrameRatesM1['time'], unit='s')
                         FrameRatesM1 = FrameRatesM1.drop('time', axis=1)
                         FrameRatesM1 = FrameRatesM1.set_index(PD.DatetimeIndex(FrameRatesM1['datetime']), drop=True)
                         LastCandle = FrameRatesM1.iloc[-1]
                         ATR = PTA.atr(high= FrameRatesM1['high'], low= FrameRatesM1['low'], close= FrameRatesM1['close'], length= 15)                             #ATR calculation

                         if ATR.iloc[-1] < 0.27 : 
                            print ("the ATR value is " ,round(ATR.iloc[-1],2) , " and less than the level limit, so the Piruz waits ...","\n")
                            return
                         else:
                            RatesM30 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M30, 0, 12)
                            if RatesM30 is not None:
                               FrameRatesM30 = PD.DataFrame(RatesM30)
                            if not FrameRatesM30.empty:
                               STH30 = PTA.stoch(high= FrameRatesM30['high'], low= FrameRatesM30['low'], close= FrameRatesM30['close'], k= 10, d= 1, smooth_k= 3)   #Stochastic calculation     
                            StochRSI = PTA.stochrsi(close= FrameRatesM1['close'],length= 14, rsi_length= 14, k= 3, d= 3)                                            #StochRSI calculation
                            StochRSI_k2 = StochRSI.iloc[-1][0]

                            Pipprofit = round(ATR.iloc[-1]* 20, 0) * 10                                                                                                  #Pip Profit
                            if Pipprofit < 100: 
                                Pipprofit = 100
                            elif Pipprofit > 400:
                                Pipprofit = 400 

                            ST1 = PTA.overlap.supertrend(high= FrameRatesM5['high'], low= FrameRatesM5['low'], close= FrameRatesM5['close'], length= 10 , multiplier= 3.3) #SuperTrend calculation
                            DirectionST1 = ST1.iloc[-2][1]
                            DirectionSTString1 = "up  " if DirectionST1 == 1.0  else "down"
                          #  if (ST1.iloc[-2][1] == 1 and ST1.iloc[-3][1] == -1) or (ST1.iloc[-2][1] == -1 and ST1.iloc[-3][1] == 1) :
                          #      CloseAllPos(self.Pair)

                            MaxBuyVol = abs((PublicVarible.RealBalance// 1000 * 1000) * PublicVarible.LossPrecent / 500)
                            MaxSellVol = abs((PublicVarible.RealBalance// 1000 * 1000) * PublicVarible.LossPrecent / 500)
                            A = AnalyzePositions()
                            if DirectionST1 == 1 : MaxBuyVol = 0.12 + (round(A[7]/2, 2))
                            elif DirectionST1 == -1 : MaxSellVol = 0.12 + (round(A[6]/2, 2))
                            print("______________________________________________________________________________________________________")
                            print(" ATR: ",round(ATR.iloc[-1],2), " StRSI:",round(StochRSI_k2,1)," SuperT M5: ", DirectionSTString1," and Price: ",round(ST1.iloc[-2][0],2),"  Stock : ",round(STH30.iloc[-1][0],1)) 
                            print("Pipprofit: ",Pipprofit ," Lotsize: ",self.CalcLotSize(ParamADX= ADX.iloc[-1][0], Point= SymbolInfo.point)," MaxBuyVol: ",round(MaxBuyVol,2)," MaxSellVol: ",round(MaxSellVol,2) )
                            CloseAllPosition(self.Pair)

                            if DirectionST1 == -1.0  :
                               if STH30.iloc[-1][0] < 20 :
                                  print("\n","Direction is Down but Stoch is -- oversold -- then volume is half !!! ")
                               if A[7] >= MaxSellVol : print("Waiting ...! Direction is Down but The sum of sells volumes is -- greater than -- the allowed volume !!! ","\n")
                               if CheckOrderIsOpen(self.Pair, LastCandle, self.TimeFrame, MT5.ORDER_TYPE_SELL, 10) == False:
                                  Base = self.FindSwingHigh(FrameRatesM1, SymbolInfo.point)    
                                  if A[7] < MaxSellVol and (StochRSI_k2 > 80 or  Base != None) :
                                     EntryPrice = SymbolInfo.bid
                                     SL = None
                                     Volume = self.CalcLotSize(ParamADX= ADX.iloc[-1][0], Point= SymbolInfo.point)
                                     if STH30.iloc[-1][0] < 20 : Volume = round(Volume/2, 2)
                                     TP1 = (EntryPrice - (Pipprofit * SymbolInfo.point)) / (SymbolInfo.point * 100)
                                     print(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                     Prompt(f"Signal {self.Pair} Type:Sell, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                     OrderSell(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"PirouzBot{PublicVarible.Id} M{str(self.TimeFrame)}")
                            
                            if DirectionST1 == 1.0 :
                               if STH30.iloc[-1][0] > 80 :
                                  print("\n","Direction is Up but Stoch is -- overbought -- then volume is half !!! ")
                               if A[6] >= MaxBuyVol : print("Wating ...! Direction is Up but The sum of Buy volumes is -- greater than -- the allowed volume !!! ","\n")
                               if CheckOrderIsOpen(self.Pair, LastCandle, self.TimeFrame, MT5.ORDER_TYPE_BUY, 10) == False:
                                  Base = self.FindSwingLow(FrameRatesM1, SymbolInfo.point)  
                                  if A[6] < MaxBuyVol and (StochRSI_k2 < 20  or Base != None) :
                                     EntryPrice = SymbolInfo.ask
                                     SL = None
                                     Volume = self.CalcLotSize(ParamADX= ADX.iloc[-1][0], Point= SymbolInfo.point)
                                     if STH30.iloc[-1][0] > 80 : Volume = round(Volume/2, 2)
                                     TP1 = (EntryPrice + (Pipprofit * SymbolInfo.point)) / (SymbolInfo.point * 100)
                                     print(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                     Prompt(f"Signal {self.Pair} Type:Buy, Volume:{Volume}, Price:{EntryPrice}, S/L:{SL}, T/P:{TP1}")
                                     OrderBuy(Pair= self.Pair, Volume= Volume, StopLoss= SL, TakeProfit= TP1, Deviation= 0, Comment= f"PirouzBot{PublicVarible.Id} M{str(self.TimeFrame)}")

########################################################################################################
      def FindSwingHigh(self, FrameRates, Point):
          Base = None
          C1 = FrameRates.iloc[-2]['high']
          C2 = FrameRates.iloc[-3]['high']
          C3 = FrameRates.iloc[-4]['high']
          if C2 > C1 and C2 > C3:
             Base = FrameRates.iloc[-3]

          if Base is None:
             return None

          BaseSizePerPoint = abs(Base['high'] - Base['low']) / Point

          if BaseSizePerPoint < 30:
             return None

          High = 0
          Low = 0
          if BaseSizePerPoint >= 30 and BaseSizePerPoint < 170:
               High = Base['high']
               Low = Base['low']
          elif BaseSizePerPoint >= 170 and BaseSizePerPoint < 210:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.75 * Point)
          elif BaseSizePerPoint >= 210 and BaseSizePerPoint < 240:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.625 * Point)
          elif BaseSizePerPoint >= 240 and BaseSizePerPoint < 290:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.5 * Point)
          elif BaseSizePerPoint >= 290 and BaseSizePerPoint < 370:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.375 * Point)
          elif BaseSizePerPoint >= 370 and BaseSizePerPoint < 530:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.25 * Point)
          elif BaseSizePerPoint >= 530 and BaseSizePerPoint < 560:
               High = Base['high']
               Low = Base['high'] - (BaseSizePerPoint * 0.1875 * Point)
          elif BaseSizePerPoint >= 560:
               return None
          
          High = round(High, 2)
          Low = round(Low, 2)

          BaseSize = abs(High - Low)
          SL = None
          TP1 = None #round((Low - BaseSize * 4.8), 2)
          TP2 = None

          print(f"Base Date Time: {Base['datetime']}")
          print(f"Base High: {High}")
          print(f"Base Low: {Low}")

          return (SL, TP1, TP2, High, Low, Base['datetime'])
########################################################################################################
      def FindSwingLow(self, FrameRates, Point):
          Base = None
          C1 = FrameRates.iloc[-2]['low']
          C2 = FrameRates.iloc[-3]['low']
          C3 = FrameRates.iloc[-4]['low']
          if C2 < C1 and C2 < C3:
             Base = FrameRates.iloc[-3]

          if Base is None:
             return None
          
          BaseSizePerPoint = abs(Base['high'] - Base['low']) / Point

          if BaseSizePerPoint < 30:
             return None

          High = 0
          Low = 0
          if BaseSizePerPoint >= 30 and BaseSizePerPoint < 170:
               High = Base['high']
               Low = Base['low']
          elif BaseSizePerPoint >= 170 and BaseSizePerPoint < 210:
               High = Base['low'] + (BaseSizePerPoint * 0.75 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 210 and BaseSizePerPoint < 240:
               High = Base['low'] + (BaseSizePerPoint * 0.625 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 240 and BaseSizePerPoint < 290:
               High = Base['low'] + (BaseSizePerPoint * 0.5 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 290 and BaseSizePerPoint < 370:
               High = Base['low'] + (BaseSizePerPoint * 0.375 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 370 and BaseSizePerPoint < 530:
               High = Base['low'] + (BaseSizePerPoint * 0.25 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 530 and BaseSizePerPoint < 560:
               High = Base['low'] + (BaseSizePerPoint * 0.1875 * Point)
               Low = Base['low']
          elif BaseSizePerPoint >= 560:
               return None
          
          High = round(High, 2)
          Low = round(Low, 2)

          BaseSize = abs(High - Low)
          SL = None
          TP1 = None #round((High + BaseSize * 4.8), 2)
          TP2 = None
          
          print(f"Base Date Time: {Base['datetime']}")
          print(f"Base High: {High}")
          print(f"Base Low: {Low}")
          return (SL, TP1, TP2, High, Low, Base['datetime'])
########################################################################################################
      def CalcLotSize(self,ParamADX, Point):
          if PublicVarible.RealBalance < 1000:
             Volume = 0.02
          else:
              A = PublicVarible.RealBalance // 1000
              Volume = round(A * 1000 / PublicVarible.LotIncreaseRatio * Point, 2)

          if ParamADX > 22.5 :
             Volume *= 2

          Volume  = round(Volume, 2)

          return Volume
########################################################################################################
def CloseAllPos(Pair:str):
 #  MT5.Close(symbol= Pair)
 #  Prompt(f"Market Status is changed to Side and All orders successfully closed, Balance: {str(PublicVarible.RealBalance)}$")
 #  PromptToTelegram(Text= f"Market Status is changed to side and All orders successfully closed" + "\n" + f"💰 Balance: {str(PublicVarible.RealBalance)}$")
    return True
########################################################################################################
def Findtrendchange(ADX) :
    Marketstatus = 0
    if ADX.iloc[-1][0] > 22 and ADX.iloc[-2][0] < 22  and ADX.iloc[-3][0] < 22 and (ADX.iloc[-4][0] < 20 or ADX.iloc[-5][0] < 20 or ADX.iloc[-6][0] < 20 or ADX.iloc[-7][0] < 20 ) : # تشخیص تبدیل بازار رنج به رونددار
       Marketstatus = 1
       return Marketstatus
    elif ADX.iloc[-1][0] < 20 and ADX.iloc[-2][0] > 20  and ADX.iloc[-3][0] > 20 and (ADX.iloc[-4][0] > 22 or ADX.iloc[-5][0] > 22 or ADX.iloc[-6][0] > 22 or ADX.iloc[-7][0] > 22 ) : # تشخیص تبدیل بازار رونددار به رنج 
        Marketstatus = 2 
        return Marketstatus
    else : return False

