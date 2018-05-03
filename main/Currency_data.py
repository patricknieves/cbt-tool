import Tor
import calendar
from crycompare import *


class Currency_data(object):
    """ Class responsible for retrieving historical exchange rates from CryptoCompare """

    def __init__(self, currency_from, currency_to):
        self.h = History()
        self.currency_data = None
        self.currency_from = currency_from
        self.currency_to = currency_to

    def get_value(self, transaction_time):
        """ Returns the value of a cryptocurrency for a given time in Dollar """
        transaction_time = calendar.timegm(transaction_time.timetuple())
        if not self.currency_data:
            Tor.change_ip()
            self.currency_data = self.h.histoHour(self.currency_from, self.currency_to, toTs=(transaction_time + 60 * 60), limit=2000)["Data"][::-1]
        for data_set in list(self.currency_data):
            # Delete Data which is older than 1 hour
            if (transaction_time - data_set["time"]) < -60*60:
                self.currency_data.remove(data_set)
                if not self.currency_data:
                    return self.get_value(transaction_time)
            # Ignore Data which is older but still not older than 1 hour
            elif (transaction_time - data_set["time"]) < 0:
                continue
            # Return rate if data set is in range of 1 hour
            elif (transaction_time - data_set["time"]) <= 60*60:
                return max(data_set["low"], data_set["high"]) - abs(data_set["low"] - data_set["high"])/2
            else:
                print ("No currency rate data found for Exchange from " + self.currency_from + " to " + self.currency_to)
                return
