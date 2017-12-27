import sys
import time
import traceback

import requests

import Tor


def get_exchange(address_from):
    Tor.change_ip()
    for attempt in range(5):
        try:
            exchange_details = requests.get("https://shapeshift.io/txStat/" + address_from).json()
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return exchange_details
    else:
        traceback.print_exc()
        sys.exit("Couldn't get transaction data from Shapeshift: " + address_from)


def get_exchanger_name(address_from, address_to):
    Tor.change_ip()
    for attempt in range(5):
        try:
            exchange_details = requests.get("https://shapeshift.io/txStat/" + address_from).json()
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            if exchange_details["status"] == "complete" and exchange_details["withdraw"] == address_to:
                return "Shapeshift"
            return "Unknown"
    else:
        traceback.print_exc()
        sys.exit("Couldn't get transaction data from Shapeshift: " + address_from)


def get_fees_shapeshift():
    Tor.change_ip()
    for attempt in range(5):
        try:
            fees = requests.get("https://shapeshift.io/marketinfo/").json()
        except:
            print ("Wait 5 sec")
            time.sleep(5)
            Tor.change_ip()
        else:
            return fees
    else:
        traceback.print_exc()
        sys.exit("Couldn't get fees from Shapeshift")


def get_exchanges_shapeshift():
    Tor.change_ip()
    for attempt in range(5):
        try:
            exchanges = requests.get("https://shapeshift.io/recenttx/50").json()
        except:
            print ("Wait 5 sec")
            time.sleep(5)
            Tor.change_ip()
        else:
            return exchanges
    else:
        traceback.print_exc()
        sys.exit("Couldn't get exchanges from Shapeshift")
