import sys
import time
import traceback

import requests

import Tor


def get_exchange(address_from):
    """ Get exchange details from Shapeshift API by sending the deposit address """
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
        if address_from:
            print("Couldn't get transaction data from Shapeshift: " + address_from)
        else:
            print("Couldn't get transaction data from Shapeshift, no output address")
        return None


def get_exchanger_name(address_from, address_to):
    """ Check if transaction is a Shapeshift transaction """
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
        return None


def get_fees_shapeshift():
    """ Returns the Shapeshift fees for all currency pairs """
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
        print("Couldn't get fees from Shapeshift")
        return None


def get_exchanges_shapeshift():
    """ Returns the recent 50 Shapeshift exchanges """
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
        print ("Couldn't get exchanges from Shapeshift")
        return None
