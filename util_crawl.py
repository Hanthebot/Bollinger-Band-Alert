import requests

def getTickers(coins=["BTC"], cur="KRW"):
    markets = ",".join([f"{cur}-{coin}" for coin in coins])
    htm = requests.get(f"https://api.upbit.com/v1/ticker?markets={markets}", headers = {"User-Agent": "Mozilla/5.0"}, timeout=5)
    data = htm.json()
    result={}
    for i in data:
        result[i["market"].split("-")[1]] = i["trade_price"]
    return result

def ohlc_ticker(data: list) -> dict:
    """ converts data (standard for chart) to ohlc format """
    ohlc = {
        "timestamp": data["timestamp"],  # into UNIX time
        "open": float(data["opening_price"]),
        "high": float(data["high_price"]),
        "low": float(data["low_price"]),
        "close": float(data["trade_price"]),
        "volume": float(data["candle_acc_trade_volume"])
    }
    return ohlc

def getCandlesOHLC(unit, candle, count, BTC="BTC", cur="KRW"):
    """
    Fetches candlestick data from the Upbit API.
    Parameters:
    unit (str): The unit of time for the candlestick data (e.g., 'minutes', 'days', 'weeks', 'months').
    candle (int): The specific time interval for the candlestick data (e.g., 1, 3, 5, 10 for minutes).
    count (int): The number of candlesticks to retrieve.
    BTC (str, optional): The base currency (default is "BTC").
    cur (str, optional): The quote currency (default is "KRW").
    Returns:
    dict: A dictionary containing the candlestick data.
    """
    htm = requests.get(f"https://api.upbit.com/v1/candles/{unit}/{candle}?market={cur}-{BTC}&count={count}", headers = {"User-Agent": "Mozilla/5.0"})
    data = htm.json()
    result = map(ohlc_ticker, data)
    return result

def getAvailable(cur="KRW"):
    resp = requests.get("https://api.upbit.com/v1/market/all", headers = {"User-Agent": "Mozilla/5.0"})
    pairs = resp.json()
    pairs = [pair["market"] for pair in pairs]
    pairs = [pair for pair in pairs if pair.split("-")[0] == cur]
    avail_list = [pair.split("-")[1] for pair in pairs]
    return avail_list
