import redis
import yfinance as yf
import threading
import atexit

#do not flush db so can keep old data 
'''
def redis_reset():
    print("Redis db resetting...")
    r.flushdb(asynchronous=True) #do not use .flushall() because it clears all databases in redis server.
'''

#this program running in background on seperate thread
try:
    r = redis.Redis(host='localhost',port=6379,db=0,decode_responses=True) #decode_responses=True is to return decoded responses
    #Redis() does not self-start up
    r.ping() #detects if it has error then handles cleanly, so atexit.register is never executed
    
    #atexit.register(redis_reset) #when closing app, reset the db
except redis.ConnectionError:
    print("Error connecting to redis data base.")
_ws_thread = None
_subscribed = set() #should be empty when first start up. will have to start_stream to get the first batch of data in
_lock = threading.Lock()

def get_prices_for_tickers(tickers: list):
    try:
        return {t: r.get("price:{}".format(t)) for t in tickers}
    except redis.ConnectionError:
        print("Error reading from redis data base.")
        return None

def _on_msg(msg): #handle incoming data from websocket
    ticker = msg.get('id')
    price = msg.get('price')
    try:
        if ticker and price:
            #r.set(key,value)
            r.set("price:{}".format(ticker),price)
    except redis.ConnectionError:
        print("Error writing to redis db.")
        return None

def start_stream(tickers: list): #first called when starting up the app, subsequently called again if update tickers
    global _ws_thread, _subscribed
    with _lock:
        new = set(tickers) - _subscribed 
        if not new:
            return 
        _subscribed.update(new)
    def _run():
        with yf.WebSocket() as ws:
            ws.subscribe(list(_subscribed))
            ws.listen(_on_msg)
    
    _ws_thread = threading.Thread(target=_run,daemon=True)
    _ws_thread.start()
        