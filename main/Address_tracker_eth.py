import Tor
import requests
import datetime
import time
import traceback
import sys

import Settings
import Currency_apis

class Address_tracker_eth(object):
    def __init__(self):
        self.shapeshift_main_address_ETH = "0x70faa28a6b8d6829a4b1e649d26ec9a2a39ba413"
        self.etherscan_key = "2BBQWBUF94KBKWQMASY3PBCGF7737FTK5N"
        self.number_of_blocks = 2000
        self.shapeshift_transactions = []
        self.possible_deposit_addresses = set()
        self.shapeshift_withdrawal_addresses = ["0xd3273eba07248020bf98a8b560ec1576a612102f",
                                            "0x3b0bc51ab9de1e5b7b6e34e5b960285805c41736",
                                            "0xeed16856d551569d134530ee3967ec79995e2051",
                                            "0x563b377a956c80d77a7c613a9343699ad6123911"]
        self.shapeshift_deposit_stop_addresses = [self.shapeshift_main_address_ETH,
                                          "0x876eabf441b2ee5b5b0554fd502a8e0600950cfa", #Bitfinex
                                          "0x32be343b94f860124dc4fee278fdcbd38c102d88", #Poloniex
                                          "0xfbb1b73c4f0bda4f67dca266ce6ef42f520fbb98", #Bittrex
                                          "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be" #Binance
                                          ]

    def filter_block(self, new_transactions):
        block = []
        if new_transactions:
            # Load Shapeshift transactions from Etherscan
            block_time = new_transactions[0]["blocktime"]
            self.delete_old_deposit_addresses(block_time)
            for new_transaction in new_transactions:
                tx_input = new_transaction["inputs"][0]["address"]
                tx_output = new_transaction["outputs"][0]["address"]
                if tx_output == self.shapeshift_main_address_ETH and not(tx_input in self.shapeshift_deposit_stop_addresses):
                    self.shapeshift_transactions.append({"from": tx_input, "delete_time": block_time})
                    self.possible_deposit_addresses.add(tx_input)
                elif tx_input in self.shapeshift_withdrawal_addresses:
                    new_transaction["is_exchange_deposit"] = False
                    new_transaction["is_exchange_withdrawl"] = True
                    block.append(new_transaction)
                elif tx_output in self.possible_deposit_addresses:
                    new_transaction["is_exchange_deposit"] = True
                    new_transaction["is_exchange_withdrawl"] = False
                    block.append(new_transaction)
        return block

    def prepare_addresses(self, endblock_ETH):
        # Load first block and get time
        block = []
        counter = 0
        while not block:
            block = Currency_apis.get_block_by_number("ETH", endblock_ETH - counter)
            counter = counter + 1
        current_exchange_time = block[0]["blocktime"]
        # Load until last shapeshift transactions 1,5 days older than the starting time
        if not self.shapeshift_transactions:
            endblock_ETH = endblock_ETH + 1
            while not self.shapeshift_transactions or current_exchange_time > \
                    datetime.datetime.utcfromtimestamp(int(self.shapeshift_transactions[-1]["timeStamp"]) - 1.5*24*60*60):
                print("Wait one second. Searching Shapeshift exchanges")
                time.sleep(1)
                old_endblock = endblock_ETH
                endblock_ETH = endblock_ETH + Settings.get_preparation_range("ETH")
                more_transactions = self.get_transactions_for_address(old_endblock, endblock_ETH)
                if more_transactions:
                    for tx in more_transactions:
                        if not(tx["from"] in self.shapeshift_deposit_stop_addresses):
                            tx["delete_time"] = datetime.datetime.utcfromtimestamp(int(tx["timeStamp"]))
                            self.shapeshift_transactions.append(tx)
                            self.possible_deposit_addresses.add(tx["from"])
            self.shapeshift_transactions = list(reversed(self.shapeshift_transactions))

        self.delete_old_deposit_addresses(current_exchange_time)

    def delete_old_deposit_addresses(self, current_exchange_time):
        # Delete transactions which are newer than 2 days
        for address_transaction in list(self.shapeshift_transactions):
            time_diff = (address_transaction["delete_time"] - current_exchange_time).total_seconds()
            if time_diff > 1.5*24*60*60:
                self.shapeshift_transactions.remove(address_transaction)
                if address_transaction["from"] in self.possible_deposit_addresses:
                    self.possible_deposit_addresses.remove(address_transaction["from"])
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