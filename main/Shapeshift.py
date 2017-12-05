import requests
import traceback
import Tor
import sys
import time


def get_exchanger(address_from, outgoing_coin):
    Tor.change_ip()
    for attempt in range(5):
        try:
            exchange_details = requests.get("https://shapeshift.io/txStat/" + address_from).json()
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            if exchange_details["status"] == "complete" and exchange_details["outgoingType"] == outgoing_coin:
                return "Shapeshift"
            return "Unknown"
    else:
        traceback.print_exc()
        sys.exit("Counldn't get transaction data from Shapeshift: " + address_from)
