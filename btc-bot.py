import websocket, json, pprint, numpy
from binance.client import Client
from binance.enums import *
import ta
import config

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.00019

closes = []

in_position = False

client = Client(config.API_KEY, config.API_SECRET)
# Greetings 

print("< PYTHON TRADING BOT FOR BTC-USDT >")
print("  ")
print(" I was developed and designed by Muhammad Faiz Khan")
print("  ")
print("  ")
print(" Trading Started -------------------------- ")
print("  ")
print("  ")


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending Order")
        order = client.create_order(symbol=symbol, side = side, type = order_type, quantity = quantity)
        print(order) 
    except Exception as e:
        return False

    return True 


def on_open(ws):
    print("opened connection")


def on_close(ws):
    print("closed connection")

    
def on_message(ws, message):
    global closes
    print("recieved message")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    
    is_candle_closed = candle['s']
    
    close = candle['c']

    if is_candle_closed:
        print("price closed at {}".format(close))
        closes.append(float(close))
        print("close")
        print(closes)
        
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = ta.RSI(np_closes, RSI_PERIOD)
            print("RSI'S Calculated :")
            print(rsi)
            last_rsi = rsi[-1]
            print("current RSI : {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell Now !")
                    # Binance Sell Logic
                    order_success = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_success:
                        is_position = False
                else:
                    print("We've nothing to own")

            if last_rsi > RSI_OVERSOLD:
                if in_position:
                    print("It's oversold now, we've nothing to do.")
                else:
                    print("Buy Now !")
                    # Binance Buy Logic
                    order_success = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_success:
                        is_position = True

ws = websocket.WebSocketApp(SOCKET, on_open= on_open, on_close= on_close, on_message= on_message)
ws.run_forever()