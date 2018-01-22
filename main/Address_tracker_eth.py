import Tor
import requests
import datetime
import time
import traceback
import sys

import Settings
import Currency_apis

class Address_tracker_eth(object):
    def __init__(self, current_block_number):
        self.shapeshift_main_address_ETH = "0x70faa28a6b8d6829a4b1e649d26ec9a2a39ba413"
        self.etherscan_key = "2BBQWBUF94KBKWQMASY3PBCGF7737FTK5N"
        self.number_of_blocks = 2000
        # Added number can/must be adapted
        self.endblock_ETH = current_block_number + Settings.get_preparation_range("ETH")
        self.shapeshift_transactions = []

    def is_shapeshift_related_as_deposit(self, exchange_transaction):
        for address_transaction in self.shapeshift_transactions:
            if exchange_transaction["blocktime"] < datetime.datetime.utcfromtimestamp(int(address_transaction["timeStamp"])):
                # Shapeshift sends deposits to main address after certain time (approx. 2 hours)
                if exchange_transaction["outputs"][0]["address"] != unicode(self.shapeshift_main_address_ETH) and \
                                exchange_transaction["outputs"][0]["address"] == str(address_transaction["from"]):
                    return True
            else:
                return False

    def is_shapeshift_related_as_withdrawl(self, exchange_transaction):
        for address_transaction in reversed(self.shapeshift_transactions):
            if exchange_transaction["blocktime"] > datetime.datetime.utcfromtimestamp(int(address_transaction["timeStamp"])):
                # Shapeshift sends money from main address to sub addresses (mostly > 400 ETH), which send withdrawls to customers
                if exchange_transaction["inputs"][0]["address"] != unicode(self.shapeshift_main_address_ETH) and \
                                exchange_transaction["inputs"][0]["address"] == str(address_transaction["to"]):
                    return True
            else:
                return False

    def check_and_save_if_shapeshift_related(self, exchange_transaction):
        self.load_new_transactions(exchange_transaction["blocktime"])
        if self.is_shapeshift_related_as_deposit(exchange_transaction):
            exchange_transaction["is_exchange_deposit"] = True
            exchange_transaction["is_exchange_withdrawl"] = False
        elif self.is_shapeshift_related_as_withdrawl(exchange_transaction):
            exchange_transaction["is_exchange_deposit"] = False
            exchange_transaction["is_exchange_withdrawl"] = True
        return exchange_transaction

    def get_block_by_number_only_shapeshift_txs(self, current_block_number):
        new_transactions = Currency_apis.get_block_by_number("ETH", current_block_number)
        block = []
        for new_transaction in new_transactions:
            transaction = self.check_and_save_if_shapeshift_related(new_transaction)
            if new_transaction["is_exchange_deposit"] or new_transaction["is_exchange_withdrawl"]:
                block.append(transaction)
        return block

    def load_new_transactions(self, current_exchange_time):
        # Load until last shapeshift transactions is 1 day older than the current transaction to check
        while not self.shapeshift_transactions or current_exchange_time < datetime.datetime.utcfromtimestamp(int(self.shapeshift_transactions[-1]["timeStamp"]) + 24*60*60):
            print("Wait one second")
            time.sleep(1)
            more_transactions = self.get_transactions_for_address(self.endblock_ETH - self.number_of_blocks, self.endblock_ETH)
            self.shapeshift_transactions.extend(more_transactions)
            self.endblock_ETH = self.endblock_ETH - self.number_of_blocks - 1

        # Delete transactions which are newer than 24 hours
        for address_transaction in list(self.shapeshift_transactions):
            if current_exchange_time < datetime.datetime.utcfromtimestamp(int(address_transaction["timeStamp"]) - 24*60*60):
                self.shapeshift_transactions.remove(address_transaction)
            else:
                break

    def get_transactions_for_address(self, startblock, endblock):
        Tor.change_ip()
        for attempt in range(5):
            try:
                transactions = requests.get("http://api.etherscan.io/api?module=account&"
                                            "action=txlist&" +
                                            "address=" + self.shapeshift_main_address_ETH +
                                            "&startblock=" + str(startblock) +
                                            "&endblock=" + str(endblock) +
                                            "&sort=desc" +
                                            "&apikey=" + self.etherscan_key).json()["result"]
            except:
                print ("Wait 5 sec")
                time.sleep(5)
                Tor.change_ip()
            else:
                return transactions
        else:
            traceback.print_exc()
            sys.exit("Couldn't get transactions from Etherscan")

    def get_exchanger_name(self, transaction_from, transaction_to):
        if transaction_from["symbol"] == "ETH":
            if self.is_shapeshift_related_as_deposit(transaction_from):
                return "Shapeshift"
        if transaction_to["symbol"] == "ETH":
            if self.is_shapeshift_related_as_withdrawl(transaction_to):
                return "Shapeshift"
        return "Unknown"