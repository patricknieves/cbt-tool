import requests
import traceback
import sys
import time
from main import Tor

class Coinmarketcap(object):
    def __init__(self):
        self.coinmarketcap_data = self.get_rates()
        self.last_update_time = time.time()

    def get_dollarvalue(self, currency):
        current_time = time.time()
        # Update data every 10 min
        if (current_time - self.last_update_time) > 10*60:
            self.coinmarketcap_data = self.get_rates()
            self.last_update_time = current_time
        for currencyData in self.coinmarketcap_data:
            if currencyData["symbol"] == currency:
                return currencyData["price_usd"]

    def get_rates(self):
        Tor.change_ip()
        for attempt in range(5):
            try:
                rates = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0").json()
            except:
                print ("Wait 5 sec")
                time.sleep(5)
                Tor.change_ip()
            else:
                return requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0").json()
        else:
            traceback.print_exc()
            sys.exit("Couldn't get exchanges from Shapeshift")
