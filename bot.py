#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
from datetime import datetime
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "SALMONSHARKS"


# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!
class MovingAverager:
    def __init__(self, window=5):
        self.queue = []
        self.window = window
    
    def add(self, e):
        if len(self.queue) < self.window:
            self.queue.append(e)
        else:
            self.queue.pop(0)
            self.queue.append(e)
    
    def get(self):
        return np.mean(self.queue)
    
    def uptrend(self):
        if len(self.queue) < self.window:
            return False
        neg_count = 0
        for i in range(1, self.window):
            if self.queue[i] - self.queue[i-1] < 0:
                neg_count += 1
        return neg_count < 0.2 * self.window
    
    def downtrend(self):
        if len(self.queue) < self.window:
            return False
        pos_count = 0
        for i in range(1, self.window):
            if self.queue[i] - self.queue[i-1] > 0:
                pos_count += 1
        return pos_count < 0.2 * self.window


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)

    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    best_price = {'BOND': {}, 'VALBZ': {}, 'VALE': {}, "GS": {}, "MS": {}, "WFC": {}, "XLF": {}}
    for id in ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]:
        best_price[id]["BID"] = 0
        best_price[id]["ASK"] = 5000

    current_holdings = {'BOND': 0, 'VALBZ': 0, 'VALE': 0, "GS": 0, "MS": 0, "WFC": 0, "XLF": 0}
    orders = {'BOND': {}, 'VALBZ': {}, 'VALE': {}, "GS": {}, "MS": {}, "WFC": {}, "XLF": {}}
    for id in ["BOND", "VALBZ", "VALE", "GS", "MS", "WFC", "XLF"]:
        orders[id]["BID"] = {}
        orders[id]["ASK"] = {}
        orders[id]["CONVERT"] = {}

    start = datetime.now()
    temp = True
    

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    order_number = 1
    orders = exchange.send_add_message(order_id=order_number, symbol="BOND", dir=Dir.BUY, price=999, size=100, orders = orders)


    order_number += 1
    orders = exchange.send_add_message(order_id=order_number, symbol="BOND", dir=Dir.SELL, price=1001, size=100, orders = orders)
    order_number += 1

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    while True:
        message = exchange.read_message()
        averager = MovingAverager(50)

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "fill":
            current_holdings = update_holdings(current_holdings, message)
            if message["symbol"] == "BOND":
                orders = update_bond_order(exchange, best_price, message, order_number, orders)
                order_number += 1
            if message["symbol"] == "VALE":
                fair_value = fair_price_vale_from_basket(best_price)
                size = message["size"]
                if message["dir"] == "BUY":
                    orders = exchange.send_add_message(order_id=order_number + 2, symbol="VALE", dir=Dir.BUY, price= fair_value - 10, size= size, orders = orders)
                else:
                    orders = exchange.send_add_message(order_id=order_number + 3, symbol="VALE", dir=Dir.SELL, price= fair_value + 10, size= size, orders = orders)
            if message["symbol"] == "VALBZ":
                fair_value = fair_price_vale_from_basket(best_price)
                size = message["size"]
                if message["dir"] == "BUY":
                    orders = exchange.send_add_message(order_id=order_number + 2, symbol="VALBZ", dir=Dir.BUY, price= fair_value - 10, size= size, orders = orders)
                else:
                    orders = exchange.send_add_message(order_id=order_number + 3, symbol="VALBZ", dir=Dir.SELL, price= fair_value + 10, size= size, orders = orders)
            
            if dir == Dir.SELL:
                msg = "BID"
            else:
                msg = "ASK"
            #oldsize = orders[message['symbol']][msg][message['order_id']][1]
            #if message['size'] >= oldsize:
            #    del orders[message['symbol']][msg][message['order_id']]
            #else:
            #    newsize = oldsize - message['size']
            #    oldorder = orders[message['symbol']][msg][message['order_id']]
            #    orders[message['symbol']][msg][message['order_id']] = [oldorder[0], newsize]
            print(message)

        elif message["type"] == "convert":
            print(message)
            current_holdings = update_convert_holdings(current_holdings, message)
        elif message["type"] == "book":
            def best_price_func(side):
                if message[side]:
                    return message[side][0][0]
            old_best_price = best_price.copy()

            best_price[message["symbol"]]["BID"] = best_price_func("buy") if best_price_func("buy") != None else best_price[message["symbol"]]["BID"]
            best_price[message["symbol"]]["ASK"] = best_price_func("sell") if best_price_func("sell") != None else best_price[message["symbol"]]["ASK"]

            if best_price != old_best_price:
                print(best_price)
            
            if message["symbol"] == 'XLF':
                current_mid_price = (best_price[message["symbol"]]["BID"] + best_price[message["symbol"]]["ASK"]) / 2
                averager.add(current_mid_price)
                if abs(current_holdings['XLF']) < 75:
                    if averager.uptrend():
                        print('uptrend, buying')
                        exchange.send_add_message(order_id=order_number+1, symbol="XLF", dir=Dir.SELL, price=best_price["XLF"]['ASK'], size=1)
                        order_number += 1
                    if averager.downtrend():
                        print('downtrend, selling')
                        exchange.send_add_message(order_id=order_number+1, symbol="XLF", dir=Dir.BUY, price=best_price["XLF"]['BID'], size=1)
                        order_number += 1
        
        if best_price["VALE"]["ASK"] < best_price["VALBZ"]["BID"] - 10:
            fair_value = fair_price_vale_from_basket(best_price)
            orders = exchange.send_convert_message(order_id = order_number + 1, symbol="VALE", dir=Dir.SELL, size = 5, orders = orders)
            orders = exchange.send_add_message(order_id=order_number + 2, symbol="VALE", dir=Dir.BUY, price = fair_value - 10, size= 5, orders = orders)
            orders = exchange.send_add_message(order_id=order_number + 3, symbol="VALBZ", dir=Dir.SELL, price = best_price["VALBZ"]["BID"], size= 5, orders = orders)
        if best_price["VALE"]["BID"] > best_price["VALBZ"]["ASK"] + 10:
            fair_value = fair_price_vale_from_basket(best_price)
            orders = exchange.send_convert_message(order_id = order_number + 1, symbol="VALE", dir=Dir.BUY,size = 1, orders = orders)
            orders = exchange.send_add_message(order_id=order_number + 2, symbol="VALE", dir=Dir.SELL, price = fair_value + 10, size= 5, orders = orders)
            orders = exchange.send_add_message(order_id=order_number + 3, symbol="VALBZ", dir=Dir.BUY, price = best_price["VALBZ"]["ASK"], size= 5, orders = orders)

        order_number += 10

        if temp and ((datetime.now() - start).total_seconds() > 1):
            fair_value = fair_price_vale_from_basket(best_price)
            orders = exchange.send_add_message(order_id=order_number, symbol="VALE", dir=Dir.BUY, price= fair_value - 10, size= 10, orders = orders)
            order_number += 1
            orders = exchange.send_add_message(order_id=order_number, symbol="VALE", dir=Dir.SELL, price= fair_value + 10, size= 10,orders = orders)
            order_number += 1
            orders = exchange.send_add_message(order_id=order_number, symbol="VALBZ", dir=Dir.BUY, price= fair_value - 10, size= 10, orders = orders)
            order_number += 1
            orders = exchange.send_add_message(order_id=order_number, symbol="VALBZ", dir=Dir.SELL, price= fair_value + 10, size= 10, orders = orders)
            order_number += 1
            temp = False



def update_bond_order(exchange, best_price, message, n, orders):
    size = message["size"]
    if message["dir"] == "BUY":
        price = min(message["price"], best_price["BOND"]["BID"], 999)
        orders = exchange.send_add_message(order_id=n, symbol="BOND", dir=Dir.BUY, price=price, size=size, orders = orders)
    if message["dir"] == "SELL":
        price = max(message["price"], best_price["BOND"]["ASK"], 1001)
        orders = exchange.send_add_message(order_id=n, symbol="BOND", dir=Dir.SELL, price=price, size=size, orders = orders)
    return orders

def update_holdings(current_holdings, message):
    if message["dir"] == "BUY":
        current_holdings[message["symbol"]] += message["size"]
    if message["dir"] == "SELL":
        current_holdings[message["symbol"]] -= message["size"]
    print(current_holdings)
    return current_holdings

def fair_price_vale_from_basket(best_price):
    def mid_price(symbol):
        return 0.5 * (best_price[symbol]['ASK'] + best_price[symbol]['BID'])

    return int((mid_price('VALBZ') + mid_price('VALE')) / 2)


def fair_price_xlf_from_basket(best_price):
    def mid_price(symbol):
        return 0.5 * (best_price[symbol]['ASK'] + best_price[symbol]['BID'])

    return int((mid_price('BOND') * 3 + mid_price('GS') * 2 + mid_price('MS') * 3 + mid_price('WFC') * 2) / 10)

def update_convert_holdings(current_holdings, message):
    if message["symbol"] == "VALE":
        if message["dir"] == "BUY":
            current_holdings["VALE"] -= message["size"]
            current_holdings["VALBZ"] += message["size"]
        if message["dir"] == "SELL":
            current_holdings["VALE"] += message["size"]
            current_holdings["VALBZ"] -= message["size"]
    if message["symbol"] == "XLF":
        if message["dir"] == "BUY":
            current_holdings["XLF"] -= message["size"]
            current_holdings["BOND"] += 3 * (message["size"] / 10)
            current_holdings["GS"] += 2 * (message["size"] / 10)
            current_holdings["MS"] += 3 * (message["size"] / 10)
            current_holdings["WFC"] += 2 * (message["size"] / 10)
        if message["dir"] == "SELL":
            current_holdings["XLF"] += message["size"]
            current_holdings["BOND"] -= 3 * (message["size"] / 10)
            current_holdings["GS"] -= 2 * (message["size"] / 10)
            current_holdings["MS"] -= 3 * (message["size"] / 10)
            current_holdings["WFC"] -= 2 * (message["size"] / 10)
    print(current_holdings)
    return current_holdings
# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        self.exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.exchange_socket.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
            self, order_id: int, symbol: str, dir: Dir, price: int, size: int, orders: dict
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )
        if dir == Dir.BUY:
            orders[symbol]["BID"][order_id] = [price, size]
        if dir == Dir.SELL:
            orders[symbol]["ASK"][order_id] = [price, size]
        return orders

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int, orders: dict):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )
        if dir == Dir.BUY:
            orders[symbol]["CONVERT"][order_id] = ["BUY", size]
        if dir == Dir.SELL:
            orders[symbol]["CONVERT"][order_id] = ["SELL", size]
        return orders

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s.makefile("rw", 1)

    def _write_message(self, message):
        json.dump(message, self.exchange_socket)
        self.exchange_socket.write("\n")

        now = time.time()
        self.message_timestamps.append(now)
        if len(
                self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    team_name = "SALMONSHARKS"
    main()
