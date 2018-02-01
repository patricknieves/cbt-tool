import Corresponding_tx
from main import Currency_apis, Database_manager, Shapeshift_api, Settings

# TODO change all API Requests with full node Requests

class Data_retriever(object):

    def __init__(self, currency, last_block_number=None, exchanges=None):
        self.currency = currency
        self.exchanges = [] if exchanges is None else exchanges
        self.current_block_number = None if last_block_number is None else last_block_number
        self.last_block_checked = None

    def prepare(self):
        self.exchanges = Database_manager.get_shapeshift_exchanges_by_currency(self.currency)
        self.current_block_number = Currency_apis.get_last_block_number(self.currency) - Settings.get_scraper_offset(self.currency)

    def find_exchanges(self):

        start_block = self.current_block_number

        if self.last_block_checked == None:
            self.last_block_checked = start_block - Settings.get_scraper_offset_for_first_iteration(self.currency)

        print("Starting with Block" + str(self.current_block_number) + "for" + self.currency)

        while self.exchanges and (self.current_block_number > self.last_block_checked):
            transactions = Currency_apis.get_block_by_number(self.currency, self.current_block_number)
            for transaction in transactions:

                for exchange in list(self.exchanges):
                    block_time_diff = (exchange["time_exchange"] - transaction["blocktime"]).total_seconds()
                    tx_time_diff = (exchange["time_exchange"] - transaction["time"]).total_seconds()
                    if tx_time_diff < -10*60:
                        break
                    elif tx_time_diff < 6*60:
                        # Note: float rounds numbers here. str used because float comparation in python not always working.
                        # This is needed if exchanges are retrieved from DB and not directly from the Shapeshift API
                        for output in transaction["outputs"]:
                            if str(float(exchange["amount_from"])) == str(float(output["amount"])):
                                exchange_details = Shapeshift_api.get_exchange(output["address"])
                                if not exchange_details:
                                    print("No output address for tx: " + transaction["hash"])
                                else:
                                    if exchange_details["status"] == "complete" and \
                                                    exchange_details["outgoingType"] == exchange["currency_to"]:
                                        #print("Found Exchange!")

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
                    elif block_time_diff >= 10*60:
                        self.exchanges.remove(exchange)
            self.current_block_number = self.current_block_number - 1
        print("Ending with Block " + str(self.current_block_number) + " for " + self.currency)
        self.last_block_checked = start_block - Settings.get_scraper_offset_last_block(self.currency)