import Corresponding_tx
from main import Currency_apis, Database_manager, Shapeshift_api

# TODO change all API Requests with full node Requests

class Data_retriever(object):

    def __init__(self, currency, last_block_number=None, exchanges=None):
        self.currency = currency
        self.exchanges = Database_manager.get_shapeshift_exchanges_by_currency(self.currency) if exchanges is None \
            else exchanges
        self.current_block_number = Currency_apis.get_last_block_number(currency) if last_block_number is None \
            else last_block_number
        print self.current_block_number

    def find_exchanges(self):
        while self.exchanges:
            transactions = Currency_apis.get_block_by_number(self.currency, self.current_block_number)
            for transaction in transactions:

                for exchange in list(self.exchanges):
                    block_time_diff = (exchange["time_exchange"] - transaction["blocktime"]).total_seconds()
                    tx_time_diff = (exchange["time_exchange"] - transaction["time"]).total_seconds()
                    if tx_time_diff < -5*60:
                        break
                    elif tx_time_diff < 6*60:
                        # Note: float rounds numbers here. str used because float comparation in python not always working.
                        # This is needed if exchanges are retrieved from DB and not directly from the Shapeshift API
                        for output in transaction["outputs"]:
                            if str(float(exchange["amount_from"])) == str(float(output["amount"])):
                                exchange_details = Shapeshift_api.get_exchange(output["address"])
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
                                                                                transaction["time"],
                                                                                transaction["blocktime"],
                                                                                self.current_block_number,
                                                                                exchange["id"]
                                                                                )
                                    Corresponding_tx.search_corresponding_transaction(exchange_details["outgoingType"],
                                                                                      exchange_details["transaction"],
                                                                                      exchange["id"])
                                    self.exchanges.remove(exchange)
                                    break
                    elif block_time_diff >= 5*60:
                        self.exchanges.remove(exchange)
            self.current_block_number = self.current_block_number - 1