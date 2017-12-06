import Database_manager
from Currency_data import Currency_data
import Currency_apis
import Shapeshift

# TODO change all API Requests with full node Requests
# TODO what to do with BTC "time"? Maybe just check in order to not go over all txs; can be done generally

class Exchange_finder(object):

    def __init__(self, currency_from, currency_to):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.current_block_number_from = Currency_apis.get_last_block_number(currency_from)
        self.transactions_from = []

    def find_exchanges(self):
        currency_data_from = Currency_data(self.currency_from, "USD")
        currency_data_to = Currency_data(self.currency_to, "USD")

        last_block_number_to = Currency_apis.get_last_block_number(self.currency_to)

        # TODO change to while loop
        for number in range(100):
            transactions_to = Currency_apis.get_block_by_number(self.currency_to, last_block_number_to - number)
            for transaction_to in transactions_to:
                self.load_txs_from(transaction_to["blocktime"])
                for transaction_from in self.transactions_from:
                    # Searching for corresponding transaction not older than 5 min
                    if (transaction_to["blocktime"] - transaction_from["blocktime"]).total_seconds() < 300:
                        # But older than 1 min
                        if (transaction_to["blocktime"] - transaction_from["blocktime"]).total_seconds() < 60:
                            transactions_from.remove(transaction_from)
                        else:
                            # Get Rate from CMC for certain block time. (Block creation time (input Currency) is used for both)
                            dollarvalue_from = currency_data_from.get_value(transaction_from["blocktime"])
                            dollarvalue_to = currency_data_to.get_value(transaction_from["blocktime"])
                            rate_cmc = dollarvalue_from/dollarvalue_to
                            # Compare Values with Rates
                            expected_output = transaction_from["amount"] * rate_cmc
                            if expected_output * 0.9 < transaction_to["amount"] < expected_output:
                                if not transaction_from["fee"]:
                                    transaction_from["fee"] = Currency_apis.get_fee_BTC(transaction_from["hash"])
                                if not transaction_to["fee"]:
                                    transaction_from["fee"] = Currency_apis.get_fee_BTC(transaction_to["hash"])
                                exchanger = Shapeshift.get_exchanger(transaction_from["address"], self.currency_to)
                                # Update DB
                                Database_manager.insert_exchange(self.currency_from,
                                                                 self.currency_to,
                                                                 transaction_from["amount"],
                                                                 transaction_to["amount"],
                                                                 transaction_from["fee"],
                                                                 transaction_to["fee"],
                                                                 (expected_output - transaction_to["amount"]),
                                                                 transaction_from["address"],
                                                                 transaction_to["address"],
                                                                 transaction_from["hash"],
                                                                 transaction_to["hash"],
                                                                 transaction_from["blocktime"].strftime('%Y-%m-%d %H:%M:%S'),
                                                                 transaction_to["blocktime"].strftime('%Y-%m-%d %H:%M:%S'),
                                                                 dollarvalue_from,
                                                                 dollarvalue_to,
                                                                 exchanger
                                                                 )
                                transactions_from.remove(transaction_from)
                                break
                    else:
                        print("Exchange not found for this Transaction: " + str(transaction_to["hash"]))
                        break

    def load_txs_from(self, transaction_time_to):
        global current_block_number_from
        global transactions_from
        global time_block_last
        # Check if BTC Array long enough. If not load more blocks until time difference of 10 min is reached
        while not time_block_last or (transaction_time_to - time_block_last).total_seconds() < 600:
            # Load new BTC transactions
            current_block_number_from = current_block_number_from - 1
            new_transactions_from = Currency_apis.get_block_by_number(self.currency_from, current_block_number_from)
            transactions_from.extend(new_transactions_from)
            time_block_last = new_transactions_from[0]["blocktime"]
        return transactions_from
