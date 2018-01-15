import datetime
from Shapeshift_fee import Shapeshift_fee
from Coinmarketcap import Coinmarketcap
from main import Database_manager, Shapeshift_api


class Shapeshift(object):

    def __init__(self):
        self.shapeshift_data = Shapeshift_fee()
        self.previous_exchanges = []
        self.duration = 0
        self.cmc = Coinmarketcap()

    def get_new_exchanges(self):
        self.standardized_new_transactions = []
        # Request last 50 Transactions from Shapeshift
        exchanges = Shapeshift_api.get_exchanges_shapeshift()

        if exchanges:
            time_first_exchange = datetime.datetime.utcfromtimestamp(exchanges[1]["timestamp"])
            time_last_exchange = datetime.datetime.utcfromtimestamp(exchanges[-1]["timestamp"])
            self.duration = time_first_exchange - time_last_exchange
            # Take BTC, ETH and LTC exchanges only
            #exchanges = [exchange for exchange in new_exchanges if
            #                          "BTC" == exchange["curIn"] or
            #                          "ETH" == exchange["curIn"] or
            #                          "LTC" == exchange["curIn"]]

            # Take new exchanges only
            new_exchanges = self.filter_exchanges(exchanges)

            if new_exchanges:
                self.previous_exchanges = new_exchanges
                for exchange in reversed(new_exchanges):
                    # Get dollar rate and current Shapeshift fees
                    dollarvalue_from = self.cmc.get_dollarvalue(exchange["curIn"])
                    dollarvalue_to = self.cmc.get_dollarvalue(exchange["curOut"])
                    fee_exchange = self.shapeshift_data.get_shapeshift_fees(exchange["curOut"])
                    time_exchange = datetime.datetime.utcfromtimestamp(exchange["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                    exchange_db_id = Database_manager.insert_shapeshift_exchange(exchange["curIn"],
                                                                exchange["curOut"],
                                                                exchange["amount"],
                                                                time_exchange,
                                                                fee_exchange,
                                                                dollarvalue_from,
                                                                dollarvalue_to
                                                                )
                    dict_item = {"id": exchange_db_id,
                                 "currency_from": exchange["curIn"],
                                 "currency_to": exchange["curOut"],
                                 "amount_from": exchange["amount"],
                                 "time_exchange": datetime.datetime.utcfromtimestamp(exchange["timestamp"])}
                    self.standardized_new_transactions.append(dict_item)
        return self.standardized_new_transactions

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
