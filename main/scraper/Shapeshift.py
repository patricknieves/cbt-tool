import datetime
from Shapeshift_fee import Shapeshift_fee
from Coinmarketcap import Coinmarketcap
from main import Database_manager, Shapeshift_api
import time


class Shapeshift(object):

    def __init__(self):
        self.shapeshift_fee_data = Shapeshift_fee()
        self.all_exchanges = []
        self.duration = 30
        self.currency_data = Coinmarketcap()

    def get_new_exchanges(self):
        # Request last 50 Transactions from Shapeshift
        new_exchanges = Shapeshift_api.get_exchanges_shapeshift()

        if new_exchanges:
            for new_exchange in new_exchanges:
                duplicate = False
                for exchange in list(self.all_exchanges):
                    if str(new_exchange["timestamp"]) == str(exchange["timestamp"]) and \
                                    str(new_exchange["amount"]) == str(exchange["amount"]) and \
                                    new_exchange["curIn"] == exchange["curIn"] and \
                                    new_exchange["curOut"] == exchange["curOut"]:
                        duplicate = True
                        break
                # Append if not retrieved already
                if duplicate == False:
                    self.all_exchanges.append(new_exchange)
            # Sort
            self.all_exchanges.sort(key=lambda x: x["timestamp"], reverse=True)

            for exchange in reversed(list(self.all_exchanges)):
                # Write to DB if exchange older (1 min) than the last new retrieved exchange
                if (exchange["timestamp"] + 60 < new_exchanges[-1]["timestamp"]):
                    # Get dollar rate and current Shapeshift fees
                    exchange["dollarvalue_from"] = self.currency_data.get_dollarvalue(exchange["curIn"])
                    exchange["dollarvalue_to"] = self.currency_data.get_dollarvalue(exchange["curOut"])
                    exchange["fee_exchange"] = self.shapeshift_fee_data.get_shapeshift_fee(exchange["curOut"])
                    time_exchange = datetime.datetime.utcfromtimestamp(exchange["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                    Database_manager.insert_shapeshift_exchange(exchange["curIn"],
                                                                exchange["curOut"],
                                                                exchange["amount"],
                                                                time_exchange,
                                                                exchange["fee_exchange"],
                                                                exchange["dollarvalue_from"],
                                                                exchange["dollarvalue_to"]
                                                                )
                    self.all_exchanges.remove(exchange)
                else:
                    break

def main():
    setup_db()
    shapeshift_manager = Shapeshift()
    while True:
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)

def setup_db():
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()

if __name__ == "__main__": main()