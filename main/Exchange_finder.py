import Database_manager
import Currency_apis
import Shapeshift_api
import datetime
import time
import Settings
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def find_exchanges(self, currencies_array):
        blocks_from = []
        transactions_to = []
        time_newest_block_dict = {}
        currency_data_dict = {}
        current_block_number_dict = {}

        start_time = time.time()
        current_search_time = start_time

        for currency in currencies_array:
            currency_data_dict[currency] = Currency_data(currency, "USD")
            current_block_number = Currency_apis.get_last_block_number(currency)
            current_block_number_dict[currency] = current_block_number
            print current_block_number

        while start_time - current_search_time < 60*60:
            # Check if Array long enough. If not load more blocks until time difference of 10 min is reached
            current_search_time = current_search_time - 10*60
            for currency in currencies_array:
                while currency not in time_newest_block_dict or time_newest_block_dict[currency] > datetime.datetime.utcfromtimestamp(current_search_time):
                    new_transactions = Currency_apis.get_block_by_number(currency, current_block_number_dict[currency])
                    if new_transactions:
                        blocks_from.append(new_transactions)
                        transactions_to.extend(new_transactions)
                        time_newest_block_dict[currency] = new_transactions[0]["blocktime"]
                    current_block_number_dict[currency] = current_block_number_dict[currency] - 1

            blocks_from.sort(key=lambda x: x[0]["blocktime"], reverse=True)
            transactions_to.sort(key=lambda x: x["time"], reverse=True)

            # Search for Transactions between two currencies
            for block_from in list(blocks_from):
                if block_from[0]["blocktime"] < datetime.datetime.utcfromtimestamp(current_search_time):
                    break
                else:
                    blocks_from.remove(block_from)
                    for transaction_from in block_from:
                        for transaction_to in list(transactions_to):
                            # TODO APIs don't return (correct) Transaction received times (ETH/LTC only Block time)
                            exchange_time_diff = (transaction_to["time"] - transaction_from["blocktime"]).total_seconds()
                            # transaction takes at least half min
                            if exchange_time_diff < Settings.get_exchange_time_lower_bound(transaction_to["symbol"]):
                                break
                            # Searching for corresponding transaction not older than X min
                            elif exchange_time_diff < Settings.get_exchange_time_higher_bound(transaction_to["symbol"]):
                                if transaction_to["symbol"] != transaction_from["symbol"]:
                                    # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                                    dollarvalue_from = currency_data_dict[transaction_from["symbol"]].get_value(transaction_from["blocktime"])
                                    dollarvalue_to = currency_data_dict[transaction_to["symbol"]].get_value(transaction_from["blocktime"])
                                    rate_cmc = dollarvalue_from/dollarvalue_to
                                    # Compare Values with Rates
                                    expected_output = transaction_from["amount"] * rate_cmc
                                    # TODO actually transaction_to["amount"] + transaction_to["fee"] (+ transaction_to["exchange_fee"]) - Problem APIs don't return (correct) fees (BTC/ETH)
                                    if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                        exchanger = Shapeshift_api.get_exchanger_name(transaction_from["address"], transaction_to["symbol"])
                                        # Update DB
                                        Database_manager.insert_exchange(transaction_from["symbol"],
                                                                         transaction_to["symbol"],
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
                            else:
                                transactions_to.remove(transaction_to)
                        else:
                            continue
                        break