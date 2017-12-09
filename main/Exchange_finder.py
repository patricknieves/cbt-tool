import Database_manager
import Currency_apis
import Shapeshift_api
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def __init__(self, currency_from, currency_to):
        self.currency_from = currency_from
        self.currency_to = currency_to

    def find_exchanges(self):
        transactions_from = []
        time_block_last = None
        currency_data_from = Currency_data(self.currency_from, "USD")
        currency_data_to = Currency_data(self.currency_to, "USD")
        current_block_number_from = Currency_apis.get_last_block_number(self.currency_from)
        last_block_number_to = Currency_apis.get_last_block_number(self.currency_to)

        # TODO change to while loop
        for number in range(100):
            transactions_to = Currency_apis.get_block_by_number(self.currency_to, last_block_number_to - number)
            for transaction_to in transactions_to:
                # Check if Array long enough. If not load more blocks until time difference of 10 min is reached
                while not time_block_last or (transaction_to["blocktime"] - time_block_last).total_seconds() < 600:
                    current_block_number_from = current_block_number_from - 1
                    new_transactions_from = Currency_apis.get_block_by_number(self.currency_from, current_block_number_from)
                    transactions_from.extend(new_transactions_from)
                    time_block_last = new_transactions_from[0]["blocktime"]
                for transaction_from in transactions_from:
                    block_time_diff = (transaction_to["blocktime"] - transaction_from["blocktime"]).total_seconds()
                    tx_time_diff = (transaction_to["time"] - transaction_from["time"]).total_seconds()
                    if block_time_diff < 60:
                        transactions_from.remove(transaction_from)
                    # Searching for corresponding transaction not older than 5 min (block time difference)
                    elif block_time_diff < 5*60 and tx_time_diff < 15*60:
                        # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
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
                            exchanger = Shapeshift_api.get_exchanger_name(transaction_from["address"], self.currency_to)
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
                        # print("Exchange not found for this Transaction: " + str(transaction_to["hash"]))
                        break
