import redis
import yfinance as yf
import threading

r = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True) #decode_responses=True is to return decoded responses

_ws_thread = None
_subscribed = set()
_lock = threading.Lock()

def get_prices_for_tickers(tickers: list):
    return {t: r.get("price:{}".format(t)) for t in tickers}

def _on_msg(msg):
    ticker = msg.get('id')
    price = msg.get('price')
    if ticker and price:
        #r.set(key,value)
        r.set("price: {}".format(ticker),price)
