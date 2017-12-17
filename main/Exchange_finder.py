import Database_manager
import Currency_apis
import Shapeshift_api
import Settings
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def __init__(self, currency_from, currency_to):
        self.currency_from = currency_from
        self.currency_to = currency_to

    def find_exchanges(self, check_until_block_nr_from=None, block_nr_from=None, block_nr_to=None):
        transactions_to = []
        time_newest_block_to = None
        currency_data_from = Currency_data(self.currency_from, "USD")
        currency_data_to = Currency_data(self.currency_to, "USD")
        current_block_number_from = Currency_apis.get_last_block_number(self.currency_from) if block_nr_from is None \
            else block_nr_from
        print current_block_number_from
        current_block_number_to = Currency_apis.get_last_block_number(self.currency_to) if block_nr_to is None \
            else block_nr_to
        print current_block_number_to
        check_until_block_nr_from = current_block_number_from - 150 if check_until_block_nr_from is None \
            else check_until_block_nr_from

        while current_block_number_from >= check_until_block_nr_from:
            print current_block_number_from
            transactions_from = Currency_apis.get_block_by_number(self.currency_from, current_block_number_from)
            for transaction_from in transactions_from:
                # Check if Array long enough. If not load more blocks until time difference of 10 min is reached
                while not time_newest_block_to or (time_newest_block_to - transaction_from["blocktime"]).total_seconds() > 0.5*60:
                    print current_block_number_to
                    new_transactions_to = Currency_apis.get_block_by_number(self.currency_to, current_block_number_to)
                    transactions_to.extend(new_transactions_to)
                    time_newest_block_to = new_transactions_to[0]["blocktime"]
                    current_block_number_to = current_block_number_to - 1
                transactions_to.sort(key=lambda x: x["time"], reverse=True)
                for transaction_to in transactions_to:
                    exchange_time_diff = (transaction_to["time"] - transaction_from["blocktime"]).total_seconds()
                    # transaction takes at least half min
                    if exchange_time_diff < 0.5*60:
                        break
                    # Searching for corresponding transaction not older than 5 min
                    elif exchange_time_diff < 5*60:
                        # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                        dollarvalue_from = currency_data_from.get_value(transaction_from["blocktime"])
                        dollarvalue_to = currency_data_to.get_value(transaction_from["blocktime"])
                        rate_cmc = dollarvalue_from/dollarvalue_to
                        # Compare Values with Rates
                        expected_output = transaction_from["amount"] * rate_cmc
                        if expected_output * 0.95 < transaction_to["amount"] < expected_output:
                            if not transaction_from["fee"] and self.currency_from == "BTC":
                                transaction_from["fee"] = Currency_apis.get_fee_BTC(transaction_from["hash"])
                            if not transaction_to["fee"] and self.currency_to == "BTC":
                                transaction_to["fee"] = Currency_apis.get_fee_BTC(transaction_to["hash"])
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
                                                             transaction_from["time"].strftime('%Y-%m-%d %H:%M:%S'),
                                                             transaction_from["blocktime"].strftime('%Y-%m-%d %H:%M:%S'),
                                                             transaction_to["time"].strftime('%Y-%m-%d %H:%M:%S'),
                                                             transaction_to["blocktime"].strftime('%Y-%m-%d %H:%M:%S'),
                                                             transaction_from["block_nr"],
                                                             transaction_to["block_nr"],
                                                             dollarvalue_from,
                                                             dollarvalue_to,
                                                             exchanger
                                                             )
                            #transactions_to.remove(transaction_to)
                            #break
                    else:
                        transactions_to.remove(transaction_to)
                else:
                    continue
                break
            current_block_number_from = current_block_number_from - 1