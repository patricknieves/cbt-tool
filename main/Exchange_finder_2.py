import Database_manager
import Currency_apis
import Shapeshift_api
import time
import Settings
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def find_exchanges(self, currencies_array):
        number_of_currencies = len(currencies_array)
        transactions_array = [[]]*number_of_currencies
        time_newest_block_array = [None]*number_of_currencies

        currency_data_array = []
        current_block_number_array = []

        start_time = time.time()
        update_time = start_time

        for currency in currencies_array:
            currency_data = Currency_data(currency, "USD")
            currency_data_array.append(currency_data)
            current_block_number = Currency_apis.get_last_block_number(currency)
            current_block_number_array.append(current_block_number)
            print current_block_number

        # TODO change proof
        while time.time() - start_time < 60*60:
            update_time = update_time - 10*60
            for count in range(number_of_currencies):
                # Check if Array long enough. If not load more blocks until time difference of 10 min is reached
                while not time_newest_block_array[count] or (time_newest_block_array[count] - update_time).total_seconds() > 0:
                    new_transactions = Currency_apis.get_block_by_number(currencies_array[count], current_block_number_array[count])
                    transactions_array[count].extend(new_transactions)
                    time_newest_block_array[count] = new_transactions[0]["blocktime"]
                    current_block_number_array[count] = current_block_number_array[count] - 1
                transactions_array[count].sort(key=lambda x: x["time"], reverse=True)

            for count_from in range(number_of_currencies):
                for count_to in [x for i,x in enumerate(range(number_of_currencies)) if i != count_from]:
                    # Search for Transactions between two currencies
                    for transaction_from in transactions_array[count_from]:
                        for transaction_to in transactions_array[count_to]:
                            exchange_time_diff = (transaction_to["time"] - transaction_from["blocktime"]).total_seconds()
                            # transaction takes at least half min
                            if exchange_time_diff < Settings.get_exchange_time_lower_bound(transaction_to["symbol"]):
                                break
                            # Searching for corresponding transaction not older than 5 min
                            elif exchange_time_diff < Settings.get_exchange_time_higher_bound(transaction_to["symbol"]):
                                # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                                dollarvalue_from = currency_data_array[count_from].get_value(transaction_from["blocktime"])
                                dollarvalue_to = currency_data_array[count_to].get_value(transaction_from["blocktime"])
                                rate_cmc = dollarvalue_from/dollarvalue_to
                                # Compare Values with Rates
                                expected_output = transaction_from["amount"] * rate_cmc
                                if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                    if not transaction_from["fee"] and transaction_from["symbol"] == "BTC":
                                        transaction_from["fee"] = Currency_apis.get_fee_BTC(transaction_from["hash"])
                                    if not transaction_to["fee"] and transaction_to["symbol"] == "BTC":
                                        transaction_to["fee"] = Currency_apis.get_fee_BTC(transaction_to["hash"])
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