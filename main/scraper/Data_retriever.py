import datetime
import Corresponding_tx
from main import Currency_apis, Database_manager, Shapeshift_api

# TODO change all API Requests with full node Requests

class Data_retriever(object):

    def __init__(self, currency, last_block_number=None):
        self.currency = currency
        self.current_block_number = Currency_apis.get_last_block_number(currency) if last_block_number is None \
            else last_block_number
        print self.current_block_number

    def find_exchanges(self):
        exchanges = Database_manager.get_shapeshift_exchanges_by_currency(self.currency)

        while exchanges:
            transactions = Currency_apis.get_block_by_number(self.currency, self.current_block_number)
            for transaction in transactions:
                for exchange in exchanges:
                    time_exchange = exchange["time_exchange"]
                    block_time_diff = (time_exchange - transaction["blocktime"]).total_seconds()
                    tx_time_diff = (time_exchange - transaction["time"]).total_seconds()
                    if block_time_diff < -120:
                        break
                    elif block_time_diff < 3*60 and tx_time_diff < 15*60:
                        if exchange["amount_from"] == transaction["amount"]:
                            exchange_details = Shapeshift_api.get_exchange(transaction["address"])
                            if exchange_details["status"] == "complete" and \
                                            exchange_details["outgoingType"] == exchange["currency_to"]:
                                if not transaction["fee"]:
                                    transaction["fee"] = Currency_apis.get_fee_BTC(transaction["hash"])
                                Database_manager.update_shapeshift_exchange(exchange_details["outgoingCoin"],
                                                                            transaction["fee"],
                                                                            exchange_details["address"],
                                                                            exchange_details["withdraw"],
                                                                            transaction["hash"],
                                                                            exchange_details["transaction"],
                                                                            transaction["blocktime"],
                                                                            self.current_block_number,
                                                                            exchange["id"]
                                                                            )
                                Corresponding_tx.search_corresponding_transaction(exchange_details["outgoingType"],
                                                                                  exchange_details["transaction"],
                                                                                  exchange["id"])
                                exchanges.remove(exchange)
                                break
                    else:
                        exchanges.remove(exchange)
            self.current_block_number = self.current_block_number - 1