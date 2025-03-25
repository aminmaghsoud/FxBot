import MetaTrader5 as MT5
from Utility import *
import PublicVarible


########################################################################################################
def OrderBuy(Pair, Volume:float, StopLoss:float = None, TakeProfit:float = None, Deviation:int = 0, Comment:str = ""):
    SymbolInfo = MT5.symbol_info(Pair)
    if SymbolInfo is None:
       print(f"Symbol {Pair} is None")
       Prompt(f"Symbol {Pair} is None")
       return

    Prompt("Buy order for {}".format(Pair))
    if PublicVarible.CanOpenOrder == True:
       if MT5.positions_total() < PublicVarible.MaxOpenTrades:
          Request = {
                     "action": MT5.TRADE_ACTION_DEAL,
                     "symbol": Pair,
                     "volume": Volume,
                     "type": MT5.ORDER_TYPE_BUY,
                     "sl": StopLoss,
                     "tp": TakeProfit,
                     "deviation": Deviation,
                     "comment": Comment,
                     "type_time": MT5.ORDER_TIME_GTC,
                     "type_filling": MT5.ORDER_FILLING_FOK
                    }
       
          if StopLoss == None:
                del Request['sl']
       
          if TakeProfit == None:
             del Request['tp']
       
          print(Request)
          Result = MT5.order_send(Request)
          Prompt("Send buy order {} {} lots with deviation={} points".format(Pair, Volume, Deviation))
          if Result.retcode != MT5.TRADE_RETCODE_DONE:
             PromptToTelegram("Order Send failed, retcode={}".format(Result.retcode))
             ResultDict = Result._asdict()
             for field in ResultDict.keys():
                 Prompt("   {}={}".format(field,ResultDict[field]))
                 if field == "request":
                    TraderequestDict=ResultDict[field]._asdict()
                    for tradereq_filed in TraderequestDict:
                         PromptToTelegram("traderequest: {}={}".format(tradereq_filed,TraderequestDict[tradereq_filed]))
          else:
             
             Prompt("Send buy order for {} done!, ".format(Pair))
             Lot = CalcTotalVolumes(Pair= Pair)
             Text = f"🔵 Buy {Pair} (#{Result.order})" + "\n" + f"Volume: {Result.volume}" + "\n" + f"Price: {Result.price}" +  "\n" + f"S/L: {StopLoss}" + "\n" + f"T/P: {TakeProfit}" + "\n" + f"⬆️ Total buy volume: {Lot[0]} lot" + "\n" + f"⬇️ Total sell volume: {Lot[1]} lot"
             print(Text)
             PromptToTelegram(Text= Text)
       else:
           Prompt("A maximum of {} orders can be open".format(PublicVarible.MaxOpenTrades))
    else:
        Prompt("Stopped opening a new order")
########################################################################################################
def OrderSell(Pair, Volume:float, StopLoss:float = None, TakeProfit:float = None, Deviation:int = 0, Comment:str = ""):
    SymbolInfo = MT5.symbol_info(Pair)
    if SymbolInfo is None:
       print(f"Symbol {Pair} is None")
       Prompt(f"Symbol {Pair} is None")
       return

    Prompt("Sell order for {}".format(Pair))
    if PublicVarible.CanOpenOrder == True:
       if MT5.positions_total() < PublicVarible.MaxOpenTrades:
          Request = {
                     "action": MT5.TRADE_ACTION_DEAL,
                     "symbol": Pair,
                     "volume": Volume,
                     "type": MT5.ORDER_TYPE_SELL,
                     "sl": StopLoss,
                     "tp": TakeProfit,
                     "deviation": Deviation,
                     "comment": Comment,
                     "type_time": MT5.ORDER_TIME_GTC,
                     "type_filling": MT5.ORDER_FILLING_FOK
                    }
          
          if StopLoss == None:
             del Request['sl']
          
          if TakeProfit == None:
             del Request['tp']
          
          print(Request)
          Result = MT5.order_send(Request)
          Prompt("Send sell order {} {} lots with deviation={} points".format(Pair, Volume, Deviation))
          if Result.retcode != MT5.TRADE_RETCODE_DONE:
             PromptToTelegram("Order Send failed, retcode={}".format(Result.retcode))
             ResultDict = Result._asdict()
             for field in ResultDict.keys():
                 Prompt("   {}={}".format(field,ResultDict[field]))
                 if field == "request":
                    TraderequestDict=ResultDict[field]._asdict()
                    for tradereq_filed in TraderequestDict:
                         PromptToTelegram("traderequest: {}={}".format(tradereq_filed,TraderequestDict[tradereq_filed]))
          else:
             Prompt("Send sell order for {} done!, ".format(Pair))
             Lot = CalcTotalVolumes(Pair= Pair)
             Text = f"🔴 Sell {Pair} (#{Result.order})" + "\n" + f"Volume: {Result.volume}" + "\n" + f"Price: {Result.price}" +  "\n" + f"S/L: {StopLoss}" + "\n" + f"T/P: {TakeProfit}" + "\n" + f"⬆️ Total buy volume: {Lot[0]} lot" + "\n" + f"⬇️ Total sell volume: {Lot[1]} lot"
             PromptToTelegram(Text= Text)
       else:
           Prompt("A maximum of {} orders can be open".format(PublicVarible.MaxOpenTrades))
    else:
        Prompt("Stopped opening a new order")
########################################################################################################
def OrderBuyStop(Pair, Volume:float, Price:float, StopLoss:float = None, TakeProfit:float = None, TypeTime = MT5.ORDER_TIME_GTC):
    Prompt("Buy stop order for {}".format(Pair))
    #if MT5.positions_total() < MaxOpenTrades:

    # Check order pending exist
    OrderExist = False
    Orders = MT5.orders_get(symbol= Pair)
    if Orders is None:
        OrderExist = False
    else:
        for Item in Orders:
            if Item.type == 4 and Item.price_open < Price:
               OrderExist = True
    
    if OrderExist == False:
       SymbolInfo = MT5.symbol_info(Pair)
       if SymbolInfo is None:
          Prompt("Symbol Info {} is None".format(Pair))
       else:
          Point = SymbolInfo.point

          SL = 0
          if StopLoss is not None:
             SL = Price - StopLoss * Point

          if TakeProfit is not None:
             TP = Price + TakeProfit * Point

          Request = {
                     "action": MT5.TRADE_ACTION_PENDING,
                     "symbol": Pair,
                     "volume": Volume,
                     "type": MT5.ORDER_TYPE_BUY_STOP,
                     "price": Price,
                     "sl": SL,
                     "tp": TP,
                     "comment": "Sent buy stop order",
                     "type_time": TypeTime,
                     "type_filling": MT5.ORDER_FILLING_RETURN
                    }

          if StopLoss == None:
             del Request['sl']

          if TakeProfit == None:
             del Request['tp']

          print(Request)
          Result = MT5.order_send(Request)
          print(Result)
          Prompt("Order Send by {} {} lots at {} with deviation={} points".format(Pair, Volume, Price))
          if Result.retcode != MT5.TRADE_RETCODE_DONE:
             Prompt("Order Send failed, retcode={}".format(Result.retcode))
             ResultDict = Result._asdict()
             for field in ResultDict.keys():
                 Prompt("   {}={}".format(field,ResultDict[field]))
                 if field == "request":
                    TraderequestDict=ResultDict[field]._asdict()
                    for tradereq_filed in TraderequestDict:
                        Prompt("traderequest: {}={}".format(tradereq_filed,TraderequestDict[tradereq_filed]))
          else:
             Prompt("Order Send for {} done!, ".format(Pair, Result))
    else:
       Prompt("Buy stop order {} is exist!, ".format(Pair))
    #else:
    #    Prompt("A maximum of {} orders can be open".format(MaxOpenTrades))
########################################################################################################
def OrderSellStop(Pair, Volume:float, Price:float, StopLoss:float = None, TakeProfit:float = None, TypeTime = MT5.ORDER_TIME_GTC):
    Prompt("Sell stop order for {}".format(Pair))
    #if MT5.positions_total() < MaxOpenTrades:

    # Check order pending exist
    OrderExist = False
    Orders = MT5.orders_get(symbol= Pair)
    if Orders is None:
        OrderExist = False
    else:
        for Item in Orders:
            if Item.type == 5 and Item.price_open > Price:
               OrderExist = True
    
    if OrderExist == False:

          SL = 0
          if StopLoss is not None:
             SL = Price + StopLoss

          if TakeProfit is not None:
             TP = Price - TakeProfit

          Request = {
                     "action": MT5.TRADE_ACTION_PENDING,
                     "symbol": Pair,
                     "volume": Volume,
                     "type": MT5.ORDER_TYPE_SELL_STOP,
                     "price": Price,
                     "sl": SL,
                     "tp": TP,
                     "comment": "Sent sell stop order",
                     "type_time": TypeTime,
                     "type_filling": MT5.ORDER_FILLING_RETURN
                    }

          if StopLoss == None:
             del Request['sl']

          if TakeProfit == None:
             del Request['tp']
          
          print(Request)
          Result = MT5.order_send(Request)
          print(Result)
          Prompt("Order Send by {} {} lots at {} with deviation={} points".format(Pair, Volume, Price))
          if Result.retcode != MT5.TRADE_RETCODE_DONE:
             Prompt("Order Send failed, retcode={}".format(Result.retcode))
             ResultDict = Result._asdict()
             for field in ResultDict.keys():
                 Prompt("   {}={}".format(field,ResultDict[field]))
                 if field == "request":
                    TraderequestDict=ResultDict[field]._asdict()
                    for tradereq_filed in TraderequestDict:
                        Prompt("traderequest: {}={}".format(tradereq_filed,TraderequestDict[tradereq_filed]))
          else:
             Prompt("Order Send for {} done!, ".format(Pair, Result))
    else:
       Prompt("Sell stop order {} is exist!, ".format(Pair))
    #else:
    #    Prompt("A maximum of {} orders can be open".format(MaxOpenTrades))
########################################################################################################
"""def OrderBuyLimit(Pair, Volume: float, EntryPrice, StopLoss, TakeProfit, Deviation):
    Prompt("Buy limit method for {}".format(Pair))

    if MT5.positions_total() < PublicVarible.MaxOpenTrades:
        Price = EntryPrice  # قیمت ورود سفارش Buy Limit

        SL = Price - StopLoss * MT5.symbol_info(Pair).point if StopLoss > 0 else 0
        TP = Price + TakeProfit * MT5.symbol_info(Pair).point if TakeProfit > 0 else 0

        Request = {
            "action": MT5.TRADE_ACTION_PENDING,
            "symbol": Pair,
            "volume": Volume,
            "price": Price,  # قیمت ورود سفارش
            "type": MT5.ORDER_TYPE_BUY_LIMIT,
            "sl": SL if StopLoss > 0 else 0,  # مقدار 0 یعنی بدون SL
            "tp": TP if TakeProfit > 0 else 0,  # مقدار 0 یعنی بدون TP
            "deviation": Deviation,
            "magic": 234000,
            "comment": "Sent buy limit order",
            "type_time": MT5.ORDER_TIME_GTC,
            "type_filling": MT5.ORDER_FILLING_RETURN
        }

        Result = MT5.order_send(Request)

        Prompt("Order sent for {}: {} lots at {} with deviation={} points".format(Pair, Volume, Price, Deviation))

        if Result.retcode != MT5.TRADE_RETCODE_DONE:
            Prompt("Order send failed, retcode={}".format(Result.retcode))
            ResultDict = Result._asdict()
            for field in ResultDict.keys():
                Prompt("   {}={}".format(field, ResultDict[field]))
                if field == "request":
                    TraderequestDict = ResultDict[field]._asdict()
                    for tradereq_field in TraderequestDict:
                        Prompt("       traderequest: {}={}".format(tradereq_field, TraderequestDict[tradereq_field]))
        else:
            Prompt("Order sent for {} done!".format(Pair))

    else:
        Prompt("A maximum of {} orders can be open".format(PublicVarible.MaxOpenTrades))"""
########################################################################################################
"""def OrderSellLimit(Pair, Volume: float, EntryPrice, StopLoss, TakeProfit, Deviation):
    Prompt("Sell limit method for {}".format(Pair))

    if MT5.positions_total() < PublicVarible.MaxOpenTrades:
        SymbolInfo = MT5.symbol_info(Pair)
        if SymbolInfo is None:
            Prompt("Symbol Info {} is None".format(Pair))
            return  # خروج از تابع در صورت نبود اطلاعات

        Point = SymbolInfo.point
        Ask = SymbolInfo.ask  # قیمت Ask برای بررسی مقدار EntryPrice

        if EntryPrice <= Ask:
            Prompt("Invalid EntryPrice: {}. Must be above Ask ({})".format(EntryPrice, Ask))
            return  # ورود نامعتبر

        SL = EntryPrice + StopLoss * Point if StopLoss > 0 else 0
        TP = EntryPrice - TakeProfit * Point if TakeProfit > 0 else 0

        Request = {
            "action": MT5.TRADE_ACTION_PENDING,
            "symbol": Pair,
            "volume": Volume,
            "type": MT5.ORDER_TYPE_SELL_LIMIT,
            "price": EntryPrice,  # مقدار قیمت ورودی اصلاح شد
            "sl": SL if StopLoss > 0 else 0,
            "tp": TP if TakeProfit > 0 else 0,
            "deviation": Deviation,
            "magic": 234000,
            "comment": "Sent sell limit order",
            "type_time": MT5.ORDER_TIME_GTC,
            "type_filling": MT5.ORDER_FILLING_RETURN
        }

        Result = MT5.order_send(Request)

        Prompt("Order sent for {}: {} lots at {} with deviation={} points".format(Pair, Volume, EntryPrice, Deviation))

        if Result.retcode != MT5.TRADE_RETCODE_DONE:
            Prompt("Order send failed, retcode={}".format(Result.retcode))
            ResultDict = Result._asdict()
            for field in ResultDict.keys():
                Prompt("   {}={}".format(field, ResultDict[field]))
                if field == "request":
                    TraderequestDict = ResultDict[field]._asdict()
                    for tradereq_field in TraderequestDict:
                        Prompt("       traderequest: {}={}".format(tradereq_field, TraderequestDict[tradereq_field]))
        else:
            Prompt("Order sent for {} done!".format(Pair))

    else:
        Prompt("A maximum of {} orders can be open".format(PublicVarible.MaxOpenTrades))"""
########################################################################################################
def OrderBuyLimit(Pair, Volume: float, EntryPrice: float, StopLoss: float = None, TakeProfit: float = None, Deviation: int = 0, Comment: str = ""):
    SymbolInfo = MT5.symbol_info(Pair)
    if SymbolInfo is None:
        print(f"Symbol {Pair} is None")
        PromptToTelegram(f"Symbol {Pair} is None")
        return

    PromptToTelegram("Buy Limit order for {}".format(Pair))

    if PublicVarible.CanOpenOrder == True:
        if MT5.positions_total() < PublicVarible.MaxOpenTrades:
            # اگر ورودی StopLoss و TakeProfit قیمت هستند، از همان استفاده می‌کنیم
            SL = StopLoss
            TP = TakeProfit
            Request = {
                "action": MT5.TRADE_ACTION_PENDING,
                "symbol": Pair,
                "volume": Volume,
                "type": MT5.ORDER_TYPE_BUY_LIMIT,
                "price": EntryPrice,
                "sl": SL,
                "tp": TP,
                "deviation": Deviation,
                "comment": Comment,
                "type_time": MT5.ORDER_TIME_GTC,
                "type_filling": MT5.ORDER_FILLING_FOK
            }

            # حذف مقادیر None
            if StopLoss is None:
                del Request['sl']

            if TakeProfit is None:
                del Request['tp']

            print(Request)
            Result = MT5.order_send(Request)
            PromptToTelegram(f"Send buy limit order for {Pair} {Volume} lots at {EntryPrice} with deviation={Deviation} points")

            if Result.retcode != MT5.TRADE_RETCODE_DONE:
                PromptToTelegram(f"Order Send failed, retcode={Result.retcode}")
                ResultDict = Result._asdict()
                for field in ResultDict.keys():
                    Prompt(f"   {field}={ResultDict[field]}")
                    if field == "request":
                        TraderequestDict = ResultDict[field]._asdict()
                        for tradereq_field in TraderequestDict:
                            PromptToTelegram(f"traderequest: {tradereq_field}={TraderequestDict[tradereq_field]}")
            else:
                PromptToTelegram(f"Send buy limit order for {Pair} done!")

                Lot = CalcTotalVolumes(Pair=Pair)
                Text = f"🔵 Buy Limit {Pair} (#{Result.order})" + "\n" + f"Volume: {Result.volume}" + "\n" + f"Price: {Result.price}" +  "\n" + f"S/L: {StopLoss}" + "\n" + f"T/P: {TakeProfit}" + "\n" + f"⬆️ Total buy volume: {Lot[0]} lot" + "\n" + f"⬇️ Total sell volume: {Lot[1]} lot"
                print(Text)
                PromptToTelegram(Text=Text)
        else:
            PromptToTelegram(f"A maximum of {PublicVarible.MaxOpenTrades} orders can be open")
    else:
        PromptToTelegram("Stopped opening a new order")
########################################################################################################
def OrderSellLimit(Pair, Volume: float, EntryPrice: float, StopLoss: float = None, TakeProfit: float = None, Deviation: int = 0, Comment: str = ""):
    SymbolInfo = MT5.symbol_info(Pair)
    if SymbolInfo is None:
        print(f"Symbol {Pair} is None")
        PromptToTelegram(f"Symbol {Pair} is None")
        return

    PromptToTelegram("Sell Limit order for {}".format(Pair))

    if PublicVarible.CanOpenOrder == True:
        if MT5.positions_total() < PublicVarible.MaxOpenTrades:
            # اگر ورودی StopLoss و TakeProfit قیمت هستند، از همان استفاده می‌کنیم
            SL = StopLoss
            TP = TakeProfit

            Request = {
                "action": MT5.TRADE_ACTION_PENDING,
                "symbol": Pair,
                "volume": Volume,
                "type": MT5.ORDER_TYPE_SELL_LIMIT,
                "price": EntryPrice,
                "sl": SL,
                "tp": TP,
                "deviation": Deviation,
                "comment": Comment,
                "type_time": MT5.ORDER_TIME_GTC,
                "type_filling": MT5.ORDER_FILLING_FOK
            }

            # حذف مقادیر None
            if StopLoss is None:
                del Request['sl']

            if TakeProfit is None:
                del Request['tp']

            print(Request)
            Result = MT5.order_send(Request)
            PromptToTelegram(f"Send sell limit order for {Pair} {Volume} lots at {EntryPrice} with deviation={Deviation} points")

            if Result.retcode != MT5.TRADE_RETCODE_DONE:
                PromptToTelegram(f"Order Send failed, retcode={Result.retcode}")
                ResultDict = Result._asdict()
                for field in ResultDict.keys():
                    PromptToTelegram(f"   {field}={ResultDict[field]}")
                    if field == "request":
                        TraderequestDict = ResultDict[field]._asdict()
                        for tradereq_field in TraderequestDict:
                            PromptToTelegram(f"traderequest: {tradereq_field}={TraderequestDict[tradereq_field]}")
            else:
                PromptToTelegram(f"Send sell limit order for {Pair} done!")

                Lot = CalcTotalVolumes(Pair=Pair)
                Text = f"🔴 Sell Limit {Pair} (#{Result.order})" + "\n" + f"Volume: {Result.volume}" + "\n" + f"Price: {Result.price}" + "\n" + f"S/L: {StopLoss}" + "\n" + f"T/P: {TakeProfit}" + "\n" + f"⬆️ Total buy volume: {Lot[0]} lot" + "\n" + f"⬇️ Total sell volume: {Lot[1]} lot"
                print(Text)
                PromptToTelegram(Text=Text)
        else:
            PromptToTelegram(f"A maximum of {PublicVarible.MaxOpenTrades} orders can be open")
    else:
        PromptToTelegram("Stopped opening a new order")

########################################################################################################
def ModifyTPSLPosition(Position, NewTakeProfit: float = None, NewStopLoss: float = None, Deviation: int = 0):
    # چک کردن اگر Position یک دیکشنری است یا یک DataFrame
    if not isinstance(Position, (dict, PD.DataFrame)):
        print("Invalid Position format. Expected a dictionary or DataFrame.")
        return

    # استفاده از ویژگی‌های موقعیت از جدول (DataFrame) یا دیکشنری
    symbol = Position.iloc[-1]['symbol'] if isinstance(Position, PD.DataFrame) else Position.get('symbol', '')
    position_type = Position.iloc[-1]['type'] if isinstance(Position, PD.DataFrame) else Position.get('type', 0)
    ticket = Position.iloc[-1]['ticket'] if isinstance(Position, PD.DataFrame) else Position.get('ticket', 0)

    SymbolInfo = MT5.symbol_info(symbol)
    if SymbolInfo is None:
        print(f"Symbol {symbol} is None")
        return

    print("Modify Take Profit and Stop Loss for {}".format(symbol))

    if position_type == MT5.POSITION_TYPE_BUY:
        Type = MT5.ORDER_TYPE_SELL
    else:
        Type = MT5.ORDER_TYPE_BUY

    Request = {
        "action": MT5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "position": ticket,
        "tp": NewTakeProfit,
        "sl": NewStopLoss,
    }

    if NewTakeProfit is None:
        del Request['tp']

    if NewStopLoss is None:
        del Request['sl']

    print(Request)
    Result = MT5.order_check(Request)
    print(Result)

    Result = MT5.order_send(Request)
    print(Result)
    return 0