import datetime
from Coinmarketcap import Coinmarketcap
from main import Database_manager, Shapeshift_api


class Shapeshift(object):

    def __init__(self):
        self.shapeshift_data = Shapeshift_api.get_fees_shapeshift()
        self.previous_exchanges = []
        self.duration = 0
        self.cmc = Coinmarketcap()

    def save_new_exchanges(self):
        # Request last 50 Transactions from Shapeshift
        new_exchanges = Shapeshift_api.get_exchanges_shapeshift()

        if new_exchanges:
            time_first_exchange = datetime.datetime.utcfromtimestamp(new_exchanges[1]["timestamp"])
            time_last_exchange = datetime.datetime.utcfromtimestamp(new_exchanges[-1]["timestamp"])
            self.duration = time_first_exchange - time_last_exchange
            # Take BTC, ETH and LTC exchanges only
            exchanges = [exchange for exchange in new_exchanges if
                                      "BTC" == exchange["curIn"] or
                                      "ETH" == exchange["curIn"] or
                                      "LTC" == exchange["curIn"]]
            # Take new exchanges only
            new_exchanges = self.filter_exchanges(exchanges)

            if new_exchanges:
                self.previous_exchanges = new_exchanges
                for exchange in reversed(new_exchanges):
                    # Get dollar rate and current SS fees
                    dollarvalue_from = self.cmc.get_dollarvalue(exchange["curIn"])
                    dollarvalue_to = self.cmc.get_dollarvalue(exchange["curOut"])
                    fee_exchange = self.get_shapeshift_fees(exchange["curOut"])
                    time_exchange = datetime.datetime.utcfromtimestamp(exchange["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                    Database_manager.insert_shapeshift_exchange(exchange["curIn"],
                                                                exchange["curOut"],
                                                                exchange["amount"],
                                                                time_exchange,
                                                                fee_exchange,
                                                                dollarvalue_from,
                                                                dollarvalue_to
                                                                )

    def get_shapeshift_fees(self, currency):
        for exchange in self.shapeshift_data:
            currency_shapeshift = exchange["pair"].split('_')[1]
            if currency_shapeshift == currency:
                return exchange["minerFee"]

    def filter_exchanges(self, exchanges):
        if self.previous_exchanges:
            i = 0
            new = True
            while new is True and i < len(exchanges):
                new = self.previous_exchanges[0]["timestamp"] < exchanges[i]["timestamp"] or \
                      self.previous_exchanges[0]["timestamp"] == exchanges[i]["timestamp"] and (
                          self.previous_exchanges[0]["curIn"] != exchanges[i]["curIn"] or
                          self.previous_exchanges[0]["curOut"] !=
                          exchanges[i]["curOut"] or self.previous_exchanges[0]["amount"] !=
                          exchanges[i]["amount"])
                i = i + 1
            if new is False and i != 0:
                count_old = len(exchanges)
                exchanges = exchanges[:(i - 1)]
        return exchanges
