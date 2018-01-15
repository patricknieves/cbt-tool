import Database_manager
import Currency_apis
import Shapeshift_api
import datetime
import time
import Settings
from Address_manager import Address_manager
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    @staticmethod
    def find_exchanges(currencies_array):
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

        # Start Address Manager with current block numbers
        address_manager = Address_manager(current_block_number_dict)

        while start_time - current_search_time < 3*60*60:
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
                print block_from[0]["block_nr"]
                # Stop searching and get more blocks if time limit exceeded
                if block_from[0]["blocktime"] < datetime.datetime.utcfromtimestamp(current_search_time):
                    break
                # Go to next Block if Blocktime is later than time of latest transaction_to
                elif block_from[0]["blocktime"] > transactions_to[0]["time"]:
                    continue
                else:
                    blocks_from.remove(block_from)
                    for transaction_from in block_from:
                        # Skip(/remove) transaction_from if not exchange related
                        if not(address_manager.is_exchange_deposit(transaction_from)):
                            continue

                        for transaction_to in list(transactions_to):
                            # TODO APIs don't return (correct) Transaction received times (ETH/LTC only Block time)
                            exchange_time_diff = (transaction_to["time"] - transaction_from["blocktime"]).total_seconds()
                            # transaction takes at least half min
                            if exchange_time_diff < Settings.get_exchange_time_lower_bound(transaction_to["symbol"]):
                                break
                            # Skip and remove transaction_to if not exchange related
                            if transaction_to["is_exchange_withdrawl"] != True and not(address_manager.is_exchange_withdrawl(transaction_to)):
                                transactions_to.remove(transaction_to)
                                continue
                            # Searching for corresponding transaction not older than X min
                            elif exchange_time_diff < Settings.get_exchange_time_upper_bound(transaction_to["symbol"]):
                                if transaction_from["symbol"] != transaction_to["symbol"]:
                                    # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                                    dollarvalue_from = currency_data_dict[transaction_from["symbol"]].get_value(transaction_from["blocktime"])
                                    dollarvalue_to = currency_data_dict[transaction_to["symbol"]].get_value(transaction_from["blocktime"])
                                    rate_cmc = dollarvalue_from/dollarvalue_to
                                    for output_transaction_from in transaction_from["outputs"]:
                                        for output_transaction_to in transaction_to["outputs"]:
                                            # Compare Values with Rates
                                            expected_output = output_transaction_from["amount"] * rate_cmc
                                            # TODO actually transaction_to["amount"] + transaction_to["fee"] (+ transaction_to["exchange_fee"]) - Problem API doesn't return (correct) fees (ETH)
                                            if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < output_transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                                exchanger = "Shapeshift"

                                                # Check if connected to Shapeshift (Method used if no filtering before)
                                                #exchanger = address_manager.get_exchanger_name(transaction_from, transaction_to)

                                                # Check if Shapeshift Exchange using Shapeshift API
                                                # exchanger = Shapeshift_api.get_exchanger_name(transaction_from["address"], transaction_to["address"])

                                                # Update DB
                                                fee_exchange = expected_output - output_transaction_to["amount"]
                                                Database_manager.insert_exchange(transaction_from["symbol"],
                                                                                 transaction_to["symbol"],
                                                                                 output_transaction_from["amount"],
                                                                                 output_transaction_to["amount"],
                                                                                 transaction_from["fee"],
                                                                                 transaction_to["fee"],
                                                                                 fee_exchange,
                                                                                 output_transaction_from["address"],
                                                                                 output_transaction_to["address"],
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
                            # Delete transactions older than X min
                            else:
                                transactions_to.remove(transaction_to)
