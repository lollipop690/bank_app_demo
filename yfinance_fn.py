import yfinance as yf

def check_validity(ticker: str):
    check=yf.Ticker(ticker)
    info=check.info

    if 'symbol' not in info:
        return False
    else:
        return True