import Database_manager
import Currency_apis
import Shapeshift_api
import datetime
import calendar
import Settings
from Address_manager import Address_manager
from Currency_data import Currency_data

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def __init__(self, currencies_array, current_block_number_dict=None):
        self.currencies_array = currencies_array
        self.current_block_number_dict = self.get_current_block_numbers(currencies_array) if current_block_number_dict is None \
            else current_block_number_dict
        # Start Address Manager with current block numbers
        self.address_manager = Address_manager(current_block_number_dict)
        self.blocks_from = []
        self.transactions_to = []
        self.time_newest_block_dict = {}
        self.currency_data_dict = {}

    def find_exchanges(self):
        # Perform Shapeshift Address recognition for BTC 700 Blocks before starting point
        #self.address_manager.prepare()

        for currency in self.currencies_array:
            # Get exchange rate data for every currency
            self.currency_data_dict[currency] = Currency_data(currency, "USD")

        # Load first blocks
        for currency in self.currencies_array:
            # TODO Handle case that empty because of filtering
            self.load_block_and_filter(currency)
        self.sort_blocks_and_transactions()

        # Set a starting time (earliest block time) and tracking time
        block_times = [x[0]["blocktime"] for x in self.blocks_from]
        start_time = calendar.timegm((min(block_times)).timetuple())
        current_search_time = start_time

        while start_time - current_search_time < 12*60*60:
            # Check if Array long enough. If not load more blocks until time difference of 10 min is reached
            current_search_time = current_search_time - 10*60
            for currency in self.currencies_array:
                while currency not in self.time_newest_block_dict or self.time_newest_block_dict[currency] > datetime.datetime.utcfromtimestamp(current_search_time):
                    self.load_block_and_filter(currency)
            self.sort_blocks_and_transactions()

            # Search for Transactions between two currencies
            for block_from in list(self.blocks_from):
                print block_from[0]["block_nr"]
                # Stop searching and get more blocks if time limit exceeded
                if block_from[0]["blocktime"] < datetime.datetime.utcfromtimestamp(current_search_time):
                    break
                # Go to next Block if Blocktime is later than time of latest transaction_to
                elif block_from[0]["blocktime"] > self.transactions_to[0]["time"]:
                    continue
                else:
                    self.blocks_from.remove(block_from)
                    # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                    dollarvalue_from = self.currency_data_dict[block_from[0]["symbol"]].get_value(block_from[0]["blocktime"])

                    for transaction_from in block_from:

                        for transaction_to in list(self.transactions_to):
                            if transaction_from["symbol"] != transaction_to["symbol"]:
                                # TODO APIs don't return (correct) Transaction received times (ETH/LTC only Block time)
                                exchange_time_diff = (transaction_to["time"] - transaction_from["blocktime"]).total_seconds()
                                # transaction takes at least half min
                                if exchange_time_diff < Settings.get_exchange_time_lower_bound(transaction_to["symbol"]):
                                    break
                                # Searching for corresponding transaction not older than X min
                                elif exchange_time_diff < Settings.get_exchange_time_upper_bound(transaction_to["symbol"]):
                                    # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                                    dollarvalue_to = self.currency_data_dict[transaction_to["symbol"]].get_value(transaction_from["blocktime"])
                                    rate_cmc = dollarvalue_from/dollarvalue_to
                                    for output_transaction_from in transaction_from["outputs"]:
                                        for output_transaction_to in transaction_to["outputs"]:
                                            # Compare Values with Rates
                                            # The expected output for Shapeshift is the (input*best rate) - set fee. For other exchanges also the transaction fee should be included!
                                            expected_output = (output_transaction_from["amount"] * rate_cmc) - Settings.get_exchanger_fee(transaction_to["symbol"]) # - transaction_to["fee"]
                                            if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < output_transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                                exchanger = "Shapeshift"

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
                                    self.transactions_to.remove(transaction_to)

    def sort_blocks_and_transactions(self):
        self.blocks_from.sort(key=lambda x: x[0]["blocktime"], reverse=True)
        self.transactions_to.sort(key=lambda x: x["time"], reverse=True)

    def load_block(self, currency):
        new_transactions = Currency_apis.get_block_by_number(currency, self.current_block_number_dict[currency])
        if new_transactions:
            self.blocks_from.append(new_transactions)
            self.transactions_to.extend(new_transactions)
            self.time_newest_block_dict[currency] = new_transactions[0]["blocktime"]
        self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - 1

    def load_block_and_filter(self, currency):
        new_transactions = self.address_manager.get_block_by_number(currency, self.current_block_number_dict[currency])
        if new_transactions:
            self.time_newest_block_dict[currency] = new_transactions[0]["blocktime"]
            transactions_from = []
            for new_transaction in new_transactions:
                if self.address_manager.is_exchange_deposit(new_transaction):
                    transactions_from.append(new_transaction)
                elif self.address_manager.is_exchange_withdrawl(new_transaction):
                    self.transactions_to.append(new_transaction)
            if transactions_from:
                self.blocks_from.append(transactions_from)
        self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - 1

    def get_current_block_numbers (self, currencies_array):
        for currency in currencies_array:
            # Get current block numbers
            current_block_number = Currency_apis.get_last_block_number(currency)
            self.current_block_number_dict[currency] = current_block_number
            print current_block_number