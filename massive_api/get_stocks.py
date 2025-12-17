from massive import RESTClient

client = RESTClient("DvppZWSJIkisnG0phTDHm0_ERz5JY9Et")

def check_stocks():
    tickers = []
    for t in client.list_tickers(
        ticker="NVDA",
        market="stocks",
        order="asc",
        limit="1",
        sort="ticker",
        ):
        tickers.append(t)
    if tickers:
        print(tickers)
    else:
        print("None available")

class CheckStocks(client):
    def __init__(self,)
        
