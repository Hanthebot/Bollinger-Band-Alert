import time
import json
import telepot
from telepot.loop import MessageLoop

from util import randString, load_userData, load_manifest, save_userData, user_default, set_user_default, check_crawl_list, verifyCandle
from util_crawl import getTickers, getCandlesOHLC, getAvailable
from bollinger import get_indicator, into_signal

light_data = {
    "invitation_code": randString(),
    "alive": True
}

price_data = {}

avail_list = getAvailable()

commands = {
        "refresh_code": "",
        "code": "",
        "add_coin": "add_coin [BTC]",
        "delete_coin":"delete_coin [BTC]",
        "my_data": "my_data",
        "candle": "candle [15m]",
        "count": "count [20]",
        "std": "std [2.0]",
        "share_bot": "",
        "help": "",
        "usage": "",
        "terminate": "",
        "white_list": "",
        "add_white": ""
    }

DELAY = 5

BOL_UP = "[{time}] {coin}: now {price:.02f} is above the upper bound {upper:.02f} of the Bollinger Band."
BOL_DOWN = "[{time}] {coin}: now {price:.02f} is below the lower bound {lower:.02f} of the Bollinger Band."
COUNT_MAX = 200

def handle_msg(chat_id, command, msg):
    if command == "help":
        bot.sendMessage(chat_id, "Available commands:\n" + ", ".join(commands.keys()))
    elif command == "usage":
        if (len(msg.split(" ")) == 1 or (msg.split(" ")[1] not in commands)):
            bot.sendMessage(chat_id, "Invalid command; try `usage [command]`")
            return
        help_command = msg.split(" ")[1]
        bot.sendMessage(chat_id, f"{help_command}: {commands[help_command]}")
    elif command == "code":
        bot.sendMessage(chat_id, light_data["invitation_code"])
    elif command == "refresh_code":
        light_data["invitation_code"] = randString()
        bot.sendMessage(chat_id, "Done: " + light_data["invitation_code"])
    elif command == "add_coin":
        if (len(msg.split(" ")) == 1 or (msg.split(" ")[1].upper() not in avail_list)):
            bot.sendMessage(chat_id, "Invalid coin")
            return
        coin = msg.split(" ")[1].upper()
        if coin in userData["userData"][str(chat_id)]["coins"]:
            bot.sendMessage(chat_id, "Already in the subscription list")
            return
        userData["userData"][str(chat_id)]["coins"].append(coin)
        check_crawl_list(userData)
        bot.sendMessage(chat_id, "coins: \n" + "\n".join(userData["userData"][str(chat_id)]["coins"]))
    elif command == "delete_coin":
        if (len(msg.split(" ")) == 1 or (msg.split(" ")[1].upper() not in avail_list)):
            bot.sendMessage(chat_id, "Invalid coin")
            return
        coin = msg.split(" ")[1].upper()
        try:
            coin_index = userData["userData"][str(chat_id)]["coins"].index(coin)
            del userData["userData"][str(chat_id)]["coins"][coin_index]
            check_crawl_list(userData)
            bot.sendMessage(chat_id, "coins: \n" + "\n".join(userData["userData"][str(chat_id)]["coins"]))
        except IndexError:
            bot.sendMessage(chat_id, "No such coin in the list")
            return
    elif command == "my_coins":
        bot.sendMessage(chat_id, "coins: \n" + "\n".join(userData["userData"][str(chat_id)]["coins"]))
    elif command == "my_data":
        bot.sendMessage(chat_id, "Data: " + json.dumps(userData["userData"][str(chat_id)], indent=4))
    elif command == "candle":
        if len(msg.split(" ")) == 1:
            bot.sendMessage(chat_id, "Candle: " + userData["userData"][str(chat_id)]["candle"])
        else:
            try:
                if verifyCandle(msg.split(" ")[1]) is None:
                    bot.sendMessage(chat_id, "Invalid candle value, valid values are: " + ",".join(list(VALID_CANDLES.keys())))
                    return
                userData["userData"][str(chat_id)]["candle"] = msg.split(" ")[1]
                save_userData(userData)
                bot.sendMessage(chat_id, "Candle set to " + msg.split(" ")[1])
            except IndexError:
                bot.sendMessage(chat_id, "Invalid candle value")
    elif command == "count":
        if len(msg.split(" ")) == 1:
            bot.sendMessage(chat_id, "Count: " + str(userData["userData"][str(chat_id)]["count"]))
        else:
            try:
                if not 0 < int(msg.split(" ")[1]) <= COUNT_MAX:
                    bot.sendMessage(chat_id, "Invalid count value, valid values are 0 < count <= " + str(COUNT_MAX))
                    return
                userData["userData"][str(chat_id)]["count"] = int(msg.split(" ")[1])
                save_userData(userData)
                bot.sendMessage(chat_id, "Count set to " + msg.split(" ")[1])
            except (IndexError, ValueError):
                bot.sendMessage(chat_id, "Invalid count value")
    elif command == "std":
        if len(msg.split(" ")) == 1:
            bot.sendMessage(chat_id, "Standard deviation: " + str(userData["userData"][str(chat_id)]["std"]))
        else:
            try:
                userData["userData"][str(chat_id)]["std"] = float(msg.split(" ")[1])
                save_userData(userData)
                bot.sendMessage(chat_id, "Standard deviation set to " + msg.split(" ")[1])
            except (IndexError, ValueError):
                bot.sendMessage(chat_id, "Invalid standard deviation value")
    elif command == "share_bot":
        bot.sendMessage(chat_id, "https://t.me/" + manifest["bot_id"])
    elif command == "terminate":
        if chat_id == manifest["developer"]:
            bot.sendMessage(chat_id, "Bye")
            light_data["alive"] = False
        else:
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")
    elif command in ["white_list", "add_white"]:
        if chat_id != manifest["developer"]:
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")
            return
        if command == "add_white":
            if (not (len(msg.split(" ")) > 1 and msg.split(" ")[1].isnumeric())):
                bot.sendMessage(chat_id, "Invalid ID")
                return
            userData["white_list"].append(int(msg.split(" ")[1]))
            save_userData(userData)
            bot.sendMessage(chat_id, "Added " + msg.split(" ")[1])
        elif command == "whitelist":
            bot.sendMessage(chat_id, "Whitelist: [" + ", ".join(userData["white_list"]) + "]")
        else:
            bot.sendMessage(chat_id, "No such command")
    else:
        bot.sendMessage(chat_id, "No such command")

def handle(msg):
    content_type, _, chat_id = telepot.glance(msg)
    if content_type == "text":
        command = msg["text"].split(" ")[0].lower()
        if chat_id in userData["subscribers"]:
            if command in commands:
                handle_msg(chat_id, command, msg["text"])
            else:
                bot.sendMessage(chat_id, "No such command, try 'help'")
        elif command == light_data["invitation_code"] or chat_id in userData["white_list"]:
            bot.sendMessage(manifest["developer"], "Access granted to " + chat_id)
            bot.sendMessage(chat_id, "Access granted")
            userData["subscribers"].append(chat_id)
            userData["userData"][str(chat_id)] = user_default(chat_id)
            save_userData(userData)
            light_data["invitation_code"] = randString()
        else:
            bot.sendMessage(manifest["developer"], chat_id + " attempted access")
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")

if __name__ == "__main__":
    manifest = load_manifest()
    userData = load_userData()
    set_user_default(userData)
    check_crawl_list(userData)

    bot = telepot.Bot(token=manifest["bot_token"])
    MessageLoop(bot, handle).run_as_thread()
    print("Running...")
    bot.sendMessage(manifest["developer"], "Setted up")
    
    while light_data["alive"]:
        # crawl coin ticker
        price_data = getTickers(userData["crawl_list"])

        # for each user
        for _, u_info in userData["userData"].items():
            for coin in u_info["coins"]:
                # crawl relevant order history
                if coin not in price_data:
                    continue
                (length, unit) = verifyCandle(u_info["candle"])
                ohlc = getCandlesOHLC(
                    unit=unit,
                    candle=length,
                    count=u_info["count"],
                    BTC=coin
                )
                bol = get_indicator(ohlc, {"period": u_info["count"], "std": u_info["std"]})
                signal = into_signal(bol, price_data[coin])
                # test against the alert condition
                if signal == 1:
                    bot.sendMessage(
                        u_info["id"], 
                        BOL_UP.format(time=time.strftime('%Y-%m-%d %H:%M:%S'), coin=coin, price=price_data[coin], upper=bol["BB_UPPER"]))
                elif signal == -1:
                    bot.sendMessage(
                        u_info["id"], 
                        BOL_DOWN.format(time=time.strftime('%Y-%m-%d %H:%M:%S'), coin=coin, price=price_data[coin], upper=bol["BB_LOWER"])
                    )
        time.sleep(DELAY)
