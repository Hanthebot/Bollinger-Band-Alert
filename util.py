import string
import random
import json
import os

"""
Returns random number code of length
"""
def randString(length = 7):
    rand = ""
    for _ in range(length):
        rand += random.choice(string.digits)
    return rand

def save_userData(userData):
    with open("userData.json", "w", encoding = "utf-8") as file:
        json.dump(userData, file, indent=4)

def load_manifest():
    if not os.path.exists("manifest.json"):
        # Set default value if data.json does not exist
        manifest = {
            "bot_token": "<telegram_token>",
            "bot_id": "<telegram_bot_id>",
            "developer": dev_chat_id,
            "developer_id": "dev_used_id"
        }
        print("Creating manifest.json...")
        # Load data from manifest.json
        with open("manifest.json", "w", encoding = "utf-8") as file:
            json.dump(manifest, file, indent=4)
    else:
        # Load data from data.json
        with open("manifest.json", "r", encoding = "utf-8") as file:
            manifest = json.load(file)
    return manifest

def load_userData():
    # Check whether data.json exists
    if not os.path.exists("userData.json"):
        # Set default value if data.json does not exist
        userData = {
            "subscribers": [DEFAULT_SUBSCRIBER],
            "white_list": [],
            "userData": {},
            "crawl_list": []
        }
        print("Creating userData.json...")
        # Load data from data.json
        save_userData(userData)
    else:
        # Load data from data.json
        with open("userData.json", "r", encoding = "utf-8") as file:
            userData = json.load(file)
    return userData

def user_default(subscriber):
    default_user = {
            "id": subscriber, 
            "coins": ["BTC"],
            "candle": "15m",
            "count": 20,
            "std": 2.0
        }
    return default_user.copy()

def set_user_default(userData: dict):
    for subscriber in userData["subscribers"]:
        if str(subscriber) not in list(userData["userData"].keys()):
            userData["userData"][str(subscriber)] = user_default(subscriber)
    save_userData(userData)

def check_crawl_list(userData: dict):
    userData["crawl_list"] = list(set([
                coin
                for user_id, user_info in userData["userData"].items()
                for coin in user_info["coins"] 
                ]))
    save_userData(userData)

TIME_UNITS = {
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks',
        'M': 'months',
        'y': 'years'
    }

VALID_CANDLES = [1, 3, 5, 10, 15, 30, 60, 240]

def verifyCandle(candle: str)->tuple:
    if len(candle) <= 1: return None
    try:
        length, unit = int(candle[:-1]), candle[-1]
    except ValueError:
        return None
    if unit == 'm' and length not in VALID_CANDLES:
        return None
    unit = TIME_UNITS.get(unit, None)
    if unit is None:
        return None
    return (length, unit)
