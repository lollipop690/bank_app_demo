import redis
import yfinance as yf
import threading

r = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True) #decode_responses=True is to return decoded responses

def get_prices_for_tickers(tickers: list):
    return {t: r.get("price:{}".format(t)) for t in tickers}

def start_stream(tickers):
    ...
