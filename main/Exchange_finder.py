import Database_manager
import Currency_apis
import Shapeshift_api
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
        self.address_manager = Address_manager(current_block_number_dict)
        self.blocks_from = []
        self.transactions_to = []
        self.time_newest_block_dict = {}
        self.currency_data_dict = {}
        self.async_requester = Async_requester()
        self.hours_to_load = 1
        self.current_exchanges_found = []

    def find_exchanges(self):
        start_preparation = time.time()
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

        #For Test
        print("Duration for Preparation :" + str(time.time() - start_preparation))
        counter = 0

        while start_time - current_search_time < 12*60*60:
            start_loop = time.time()
            # Check if Array long enough. If not load more blocks until time difference of 60 min is reached
            current_search_time = current_search_time - (self.hours_to_load * (60 * 60))

            self.load_blocks(current_search_time)

            # Search for Transactions between two currencies
            for block_from in list(self.blocks_from):
                start_block = time.time()
                #print "Analyzing block for " + block_from[0]["symbol"] + " nr. " + str(block_from[0]["block_nr"]) + ", lenght: " + str(len(block_from))
                # Stop searching and get more blocks if time limit exceeded
                if block_from[0]["blocktime"] < datetime.datetime.utcfromtimestamp(current_search_time):
                    break
                # Go to next Block if Blocktime is later than time of latest transaction_to
                elif block_from[0]["blocktime"] > self.transactions_to[0]["time"]:
                    self.blocks_from.remove(block_from)
                    continue
                else:
                    # Delete transactions older than 15 min
                    for transaction_to in list(self.transactions_to):
                        exchange_processing_time = (transaction_to["time"] - block_from[0]["blocktime"]).total_seconds()
                        if  exchange_processing_time > Settings.get_exchange_time_upper_bound(None):
                            # Delete transactions older than X min
                            self.transactions_to.remove(transaction_to)
                        else:
                            break

                    self.blocks_from.remove(block_from)
                    # Get Rate from CMC for certain block time. (Block creation time (input currency) is used for both)
                    dollarvalue_from = self.currency_data_dict[block_from[0]["symbol"]].get_value(block_from[0]["blocktime"])

                    #Asyncronous comparing
                    start_async = time.time()
                    threads = list(self.async_search(block_from, dollarvalue_from))
                    map(threading.Thread.start, threads)
                    map(threading.Thread.join, threads)
                    print("Duration for async comparison " + str(time.time() - start_async))

                    start_save_to_db = time.time()
                    for exchange in self.current_exchanges_found:
                        transaction_from = exchange["transaction_from"]
                        transaction_to = exchange["transaction_to"]
                        output_transaction_from = exchange["output_transaction_from"]
                        output_transaction_to = exchange["output_transaction_to"]
                        fee_exchange = exchange["fee_exchange"]
                        dollarvalue_from = exchange["dollarvalue_from"]
                        dollarvalue_to = exchange["dollarvalue_to"]
                        exchanger = exchange["exchanger"]
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
                    print("Duration for db save " + str(time.time() - start_save_to_db))
                print("Block analysis time: " + str(time.time() - start_block))
            # For Test
            counter = counter + 1
            print("Duration for Loop " + str(counter) + ": " + str(time.time() - start_loop))

    def async_search(self, block_from, dollarvalue_from):
        self.current_exchanges_found = []
        for transaction_from in block_from:
            t = Thread(target=self.compare, args=(transaction_from, dollarvalue_from))
            yield t

    def load_blocks(self, current_search_time):
        load_more = True
        while load_more:
            load_more = False
            for currency in self.currencies_array:
                if currency not in self.time_newest_block_dict or self.time_newest_block_dict[currency] > datetime.datetime.utcfromtimestamp(current_search_time):
                    # mark that has to be loaded
                    number_of_blocks = self.hours_to_load * Settings.get_block_number_for_hour(currency)
                    self.async_requester.add_request_data(currency, self.current_block_number_dict[currency], number_of_blocks)
                    self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - number_of_blocks
                    load_more = True
            if load_more:
                start = time.time()
                # load blocks
                new_blocks = self.async_requester.get_multiple_blocks_all_currencies()
                # Pass blocks to filtering
                self.filter_all(new_blocks)
                print("Block Loading Duration: " + str(time.time() - start))
        self.sort_blocks_and_transactions()

        # for currency in self.currencies_array:
        #     while currency not in self.time_newest_block_dict or self.time_newest_block_dict[currency] > datetime.datetime.utcfromtimestamp(current_search_time):
        #         start = time.time()
        #         self.load_blocks_and_filter(currency, self.hours_to_load * Settings.get_block_number_for_hour(currency))
        #         print("Block Loading Duration for " + currency + ": " + str(time.time() - start))
        # self.sort_blocks_and_transactions()

    def compare(self, transaction_from, dollarvalue_from):

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
                            fee_exchange = Settings.get_exchanger_fee(transaction_to["symbol"])
                            expected_output = (output_transaction_from["amount"] * rate_cmc) - fee_exchange # - transaction_to["fee"]
                            if expected_output * Settings.get_rate_lower_bound(transaction_to["symbol"]) < output_transaction_to["amount"] < expected_output * Settings.get_rate_upper_bound(transaction_to["symbol"]):
                                exchanger = "Shapeshift"

                                # Update DB
                                self.current_exchanges_found.append({"transaction_from": transaction_from,
                                                                     "transaction_to": transaction_to,
                                                                     "output_transaction_from":output_transaction_from,
                                                                     "output_transaction_to": output_transaction_to,
                                                                     "fee_exchange": fee_exchange,
                                                                     "dollarvalue_from": dollarvalue_from,
                                                                     "dollarvalue_to": dollarvalue_to,
                                                                     "exchanger": exchanger})



    def sort_blocks_and_transactions(self):
        self.blocks_from.sort(key=lambda x: x[0]["blocktime"], reverse=True)
        self.transactions_to.sort(key=lambda x: x["time"], reverse=True)

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

    def load_blocks_and_filter(self, currency, number_of_blocks):
        new_blocks = self.address_manager.get_blocks_by_number(currency, self.current_block_number_dict[currency], number_of_blocks)
        for new_block in new_blocks:
            if new_block:
                self.time_newest_block_dict[currency] = new_block[0]["blocktime"]
                transactions_from = []
                for new_transaction in new_block:
                    if self.address_manager.is_exchange_deposit(new_transaction):
                        transactions_from.append(new_transaction)
                    elif self.address_manager.is_exchange_withdrawl(new_transaction):
                        self.transactions_to.append(new_transaction)
                if transactions_from:
                    self.blocks_from.append(transactions_from)
        self.current_block_number_dict[currency] = self.current_block_number_dict[currency] - number_of_blocks

    def filter_all(self, new_blocks):
        def start_threads():
            for currency in self.currencies_array:
                exchanges = [block for block in new_blocks if currency == block[0]["symbol"]]
                t = Thread(target=self.filter_one_currency, args=(exchanges,))
                yield t

        threads = list(start_threads())
        map(threading.Thread.start, threads)
        map(threading.Thread.join, threads)


    def filter_one_currency(self, new_blocks_one_currency):
        for block in new_blocks_one_currency:
            new_filtered_block = self.address_manager.filter_block(block)
            if new_filtered_block:
                self.time_newest_block_dict[new_filtered_block[0]["symbol"]] = new_filtered_block[0]["blocktime"]
                transactions_from = []
                for new_transaction in new_filtered_block:
                    if self.address_manager.is_exchange_deposit(new_transaction):
                        transactions_from.append(new_transaction)
                    elif self.address_manager.is_exchange_withdrawl(new_transaction):
                        self.transactions_to.append(new_transaction)
                if transactions_from:
                    self.blocks_from.append(transactions_from)


    def get_current_block_numbers (self, currencies_array):
        for currency in currencies_array:
            # Get current block numbers
            current_block_number = Currency_apis.get_last_block_number(currency)
            self.current_block_number_dict[currency] = current_block_number
            print current_block_number