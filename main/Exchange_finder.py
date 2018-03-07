import Database_manager
import Currency_apis
import time
import threading
import datetime
import calendar
import Settings
from Address_manager import Address_manager
from Currency_data import Currency_data
from async_requests import Async_requester
from threading import Thread

# TODO change all API Requests with full node Requests


class Exchange_finder(object):

    def __init__(self, currencies_array, current_block_number_dict=None):
        self.currencies_array = currencies_array
        self.current_block_number_dict = self.get_current_block_numbers(currencies_array) if current_block_number_dict is None \
            else current_block_number_dict
        # Start Address Manager with current block numbers
        self.address_manager = Address_manager()
        self.blocks_from = []
        self.transactions_to = []
        self.time_newest_block_dict = {}
        self.currency_data_dict = {}
        self.async_requester = Async_requester()
        self.hours_single_loop = 1
        self.hours_whole_analysis = 12
        self.current_exchanges_found_one_block = []
        self.current_exchanges_found = []
        for currency in self.currencies_array:
            # Get exchange rate data for every currency
            self.currency_data_dict[currency] = Currency_data(currency, "USD")

    def find_exchanges(self):
        start_preparation = time.time()

        # Perform Shapeshift Address recognition for BTC 700 Blocks before starting point
        self.address_manager.prepare(self.current_block_number_dict)

        # Load first blocks
        self.load_first_blocks()

        # Set times
        range_to_analyze = self.hours_whole_analysis * (60 * 60)
        analysis_time_range = self.hours_single_loop * (60 * 60)
        start_time = self.get_min_blocktime()
        current_search_time = start_time

        #For Test
        print("Duration for Preparation :" + str(time.time() - start_preparation))
        counter = 0

        while start_time - current_search_time < range_to_analyze:
            start_loop = time.time()

            # Check if Array long enough. If not load more blocks until time difference of X min is reached
            current_search_time = current_search_time - analysis_time_range
            self.load_blocks(current_search_time)

            # Search for Transactions between two currencies
            for block_from in list(self.blocks_from):
                current_block_time = block_from[0]["blocktime"]
                newest_transaction_time = self.transactions_to[0]["time"]
                if current_block_time < datetime.datetime.utcfromtimestamp(current_search_time):
                    # Stop searching and get more blocks if time limit exceeded
                    break
                elif current_block_time > newest_transaction_time:
                    # Delete block and go to next one if Blocktime is later than time of newest withdrawal
                    self.blocks_from.remove(block_from)
                else:
                    # Delete all withdrawal transactions which won't be needed anymore
                    self.delete_old_withdrawals(block_from)
                    # Asyncronous comparing
                    self.async_comparing(block_from)
                    # Remove block
                    self.blocks_from.remove(block_from)
            # Save all found exchanges in the DB
            self.save_found_exchanges()

            # For Test
            counter = counter + 1
            print("Duration for Loop " + str(counter) + ": " + str(time.time() - start_loop))

    def load_first_blocks(self):
        while not self.blocks_from:
            for currency in self.currencies_array:
                self.async_requester.add_request_data(currency, self.current_block_number_dict[currency], 1)
                self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - 1
            # load blocks
            new_blocks = self.async_requester.get_multiple_blocks_all_currencies()
            # Pass blocks to filtering
            self.filter_all_and_save(new_blocks)
            # Sort
            self.sort_blocks_and_transactions()

    def get_min_blocktime(self):
        # Set a starting time (earliest block time) and tracking time
        block_times = [x[0]["blocktime"] for x in self.blocks_from]
        start_time = calendar.timegm((min(block_times)).timetuple())
        return start_time

    def save_found_exchanges(self):
        if self.current_exchanges_found:
            Database_manager.insert_multiple_exchanges(self.current_exchanges_found)
            self.current_exchanges_found = []

    def delete_old_withdrawals(self, block_from):
        # Delete transactions older than 15 min
        for transaction_to in list(self.transactions_to):
            exchange_processing_time = (transaction_to["time"] - block_from[0]["blocktime"]).total_seconds()
            if exchange_processing_time > Settings.get_exchange_time_upper_bound(None):
                # Delete transactions older than X min
                self.transactions_to.remove(transaction_to)
            else:
                break

    def load_blocks(self, current_search_time):
        load_more = True
        while load_more:
            load_more = False
            for currency in self.currencies_array:
                if currency not in self.time_newest_block_dict or self.time_newest_block_dict[currency] > datetime.datetime.utcfromtimestamp(current_search_time):
                    # mark that has to be loaded
                    number_of_blocks = self.hours_single_loop * Settings.get_block_number_for_hour(currency)
                    self.async_requester.add_request_data(currency, self.current_block_number_dict[currency], number_of_blocks)
                    self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - number_of_blocks
                    load_more = True
            if load_more:
                start = time.time()
                # load blocks
                new_blocks = self.async_requester.get_multiple_blocks_all_currencies()
                # Pass blocks to filtering
                self.filter_all_and_save(new_blocks)
                print("Block Loading Duration: " + str(time.time() - start))
        self.sort_blocks_and_transactions()

    def async_comparing(self, block_from, dollarvalue_from):
        # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
        dollarvalue_from = self.currency_data_dict[block_from[0]["symbol"]].get_value(block_from[0]["blocktime"])
        threads = list(self.async_search(block_from, dollarvalue_from))
        map(threading.Thread.start, threads)
        map(threading.Thread.join, threads)
        # Sort by address and save to final list
        self.current_exchanges_found_one_block.sort(key=lambda x: x[7])
        self.current_exchanges_found.extend(self.current_exchanges_found_one_block)
        self.current_exchanges_found_one_block = []

    def async_search(self, block_from, dollarvalue_from):
        for transaction_from in block_from:
            t = Thread(target=self.compare, args=(transaction_from, dollarvalue_from))
            yield t

    def compare(self, transaction_from, dollarvalue_from):
        for transaction_to in list(self.transactions_to):
            if transaction_from["symbol"] != transaction_to["symbol"]:
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
                        # Compare Values with Rates - The expected output for Shapeshift is the (input*best rate) - set fee. For other exchanges also the transaction fee should be included!
                        fee_exchange = Settings.get_exchanger_fee(transaction_to["symbol"])
                        expected_output = (output_transaction_from["amount"] * rate_cmc) - fee_exchange # - transaction_to["fee"]
                        for output_transaction_to in transaction_to["outputs"]:
                            if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < output_transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                exchanger = "Shapeshift"
                                # Save found exchange
                                self.current_exchanges_found_one_block.append((transaction_from["symbol"],
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
                                                                 ))

    def sort_blocks_and_transactions(self):
        self.blocks_from.sort(key=lambda x: x[0]["blocktime"], reverse=True)
        self.transactions_to.sort(key=lambda x: x["time"], reverse=True)

    def filter_all_and_save(self, new_blocks):
        def start_threads():
            for currency in self.currencies_array:
                exchanges = [block for block in new_blocks if currency == block[0]["symbol"]]
                t = Thread(target=self.filter_one_currency_and_save, args=(exchanges,))
                yield t
        threads = list(start_threads())
        map(threading.Thread.start, threads)
        map(threading.Thread.join, threads)

    def filter_one_currency_and_save(self, new_blocks_one_currency):
        for block in new_blocks_one_currency:
            new_filtered_block = self.address_manager.filter_block_and_save_addresses(block)
            if new_filtered_block:
                self.time_newest_block_dict[new_filtered_block[0]["symbol"]] = new_filtered_block[0]["blocktime"]
                transactions_from = []
                for new_transaction in new_filtered_block:
                    if new_transaction["is_exchange_deposit"]:
                        transactions_from.append(new_transaction)
                    elif new_transaction["is_exchange_withdrawl"]:
                        self.transactions_to.append(new_transaction)
                if transactions_from:
                    self.blocks_from.append(transactions_from)

    def get_current_block_numbers (self, currencies_array):
        for currency in currencies_array:
            # Get current block numbers
            current_block_number = Currency_apis.get_last_block_number(currency)
            self.current_block_number_dict[currency] = current_block_number
            print current_block_number