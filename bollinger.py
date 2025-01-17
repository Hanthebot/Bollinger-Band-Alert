""" module for OHLC, dataframe, indicator handling """

import pandas as pd
import json
from finta import TA

def get_ohlc(ohlc: map) -> pd.DataFrame:
    """ converts data (standard for chart) to DataFrame """
    df = pd.DataFrame(ohlc)
    df.set_index("timestamp", inplace=True)
    return df

def get_indicator(data: map, parameter: dict = None) -> dict:
    """
    Computes indicator from data
    Args:
        data (map): Data crawled from API provider
        parameter (dict): Stores the parameters for the indicator.
    Returns:
        map: requested indicator in pd.DataFrame format.
    """
    for param in ["period", "std"]:
        assert param in parameter
    df = get_ohlc(data)
    indicator = TA.BBANDS(df, period=parameter["period"], std_multiplier=parameter["std"])
    indicator = indicator.dropna()
    bol = json.loads(indicator.to_json(orient="records"))[0]

    return bol

def into_signal(bol: dict, price) -> int:
    """
    Computes signal from data: uppermost layer
    Args:
        bol (dict): indicator, in dict format
    Returns:
        signal in int format.
        0 denotes nothing, 1 denotes hitting upperbound, -1 denotes hitting lowerbound
    """
    if price >= bol["BB_UPPER"]:
        return 1
    if price <= bol["BB_LOWER"]:
        return -1
    return 0
