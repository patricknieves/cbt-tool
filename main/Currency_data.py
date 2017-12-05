from crycompare import *
import Tor


class Currency_data(object):

    def __init__(self, currency_in, currency_out,):
        self.h = History()
        self.history = None
        self.currency_in = currency_in
        self.currency_out = currency_out

    def get_value(self, transaction_time):
        if not self.history:
            Tor.change_ip()
            self.history = self.h.histoHour(self.currency_in, self.currency_out, toTs=transaction_time, limit=2000)["Data"][::-1]
        for data_set in self.history:
            #Delete Data which is older than 1 hour
            if (transaction_time - data_set["time"]) < -3600:
                self.history.remove(data_set)
                if not self.history:
                    return self.get_value(transaction_time)
            elif (transaction_time - data_set["time"]) > 0 and (transaction_time - data_set["time"]) <= 3600:
                return max(data_set["low"], data_set["high"]) - abs(data_set["low"] - data_set["high"])/2
            else:
                print ("No currency rate data found for Exchange from " + self.currency_in + " to " + self.currency_out)
                return