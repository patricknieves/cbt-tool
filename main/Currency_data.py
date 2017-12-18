import Tor
import time
from crycompare import *


class Currency_data(object):

    def __init__(self, currency_from, currency_to):
        self.h = History()
        self.history = None
        self.currency_from = currency_from
        self.currency_to = currency_to

    def get_value(self, transaction_time):
        transaction_time = time.mktime(transaction_time.timetuple())
        if not self.history:
            Tor.change_ip()
            self.history = self.h.histoHour(self.currency_from, self.currency_to, toTs=transaction_time, limit=2000)["Data"][::-1]
        for data_set in list(self.history):
            # Delete Data which is older than 1 hour
            if (transaction_time - data_set["time"]) < -3600:
                self.history.remove(data_set)
                if not self.history:
                    return self.get_value(transaction_time)
            elif 0 < (transaction_time - data_set["time"]) <= 3600:
                return max(data_set["low"], data_set["high"]) - abs(data_set["low"] - data_set["high"])/2
            else:
                print ("No currency rate data found for Exchange from " + self.currency_from + " to " + self.currency_to)
                return