import Database_manager
import Currency_apis
import Settings
import time
from async_requests import Async_requester


class Address_tracker_btc(object):
    def __init__(self):
        #self.shapeshift_main_addresses = set(Database_manager.get_all_shapeshift_addresses_btc())

        self.shapeshift_main_addresses = [
                                     "1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG", #Bittrex
                                     "1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk", #Bitfinex
                                     "1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM", #Poloniex
                                     "17NqGW6HY3f2LY7wFkEDn9yXpq8LWMRMEQ", #Binance #new
                                     "3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B", #Storage Address
                                    "1E57TDxSju3AEecoUjjQKkbGWAitP12znn", #Unkonwn #feb #new
                                    "1jhbBbDRdezEZ5tSsHZwuUg85Hhf4rWuz", #Unknown
                                    "1HFyPNX9gEvGHNCR34hkiseTLj2MXmqYr7",
                                    "1BiX4SkXd97AvjvTbGN1V9ykTtYf9EVXN5",
                                    "3N1f4Hv4dmMkFCyvAqu3M4wcQQYNJvs232", #feb # connections:1
                                    "17JnGQUbpqosaFZ7P3ywHQj6G75kERBSXa", # connetions: 0
                                    "1BngmLiuiXbzSNpwQ9kEbMy1KZ6xj5Jxs4" #feb
                                     ]
        #self.shapeshift_main_addresses = Settings.get_main_addresses()

        #"1E57TDxSju3AEecoUjjQKkbGWAitP12znn", #Unkonwn #feb
        #"1jhbBbDRdezEZ5tSsHZwuUg85Hhf4rWuz", #Unknown

        #"1HFyPNX9gEvGHNCR34hkiseTLj2MXmqYr7",
        #"1BiX4SkXd97AvjvTbGN1V9ykTtYf9EVXN5",
        #"17JnGQUbpqosaFZ7P3ywHQj6G75kERBSXa",
        #"1By2vSBudu7fSt7aeAR5tJza6HiGUhVcdJ", #feb
        #"3N1f4Hv4dmMkFCyvAqu3M4wcQQYNJvs232", #feb
        #"1BngmLiuiXbzSNpwQ9kEbMy1KZ6xj5Jxs4" #feb

        #"1By2vSBudu7fSt7aeAR5tJza6HiGUhVcdJ", #feb #not a SS address - unknown inputs

        #self. shapeshift_middle_addresses = set([])
        #self. shapeshift_single_addresses = set([])

        self. shapeshift_middle_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("middle")
        self. shapeshift_single_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("single")
        self.shapeshift_stop_addresses = ["1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7"]

    def check_and_save_if_shapeshift_related(self, exchange_transaction):
            for tx_output in exchange_transaction["outputs"]:
                if tx_output["address"] in self.shapeshift_main_addresses \
                        or tx_output["address"] in self.shapeshift_middle_addresses \
                        or tx_output["address"] in self.shapeshift_single_addresses:
                    if tx_output["address"][0] != "3" or tx_output["address"] in self.shapeshift_main_addresses:
                        # Delete Shapeshift Address from Outputs (and leave only User Address(es))
                        exchange_transaction["outputs"].remove(tx_output)

                        exchange_transaction["is_exchange_deposit"] = False
                        exchange_transaction["is_exchange_withdrawl"] = True

                        # Check if input address was already used and move from single to middle class.
                        if len(exchange_transaction["inputs"]) == 1 and exchange_transaction["inputs"][0]["address"] in self.shapeshift_single_addresses:
                            self.shapeshift_single_addresses.remove(exchange_transaction["inputs"][0]["address"])
                            self.shapeshift_middle_addresses.add(exchange_transaction["inputs"][0]["address"])
                        else:
                            for tx_input in exchange_transaction["inputs"]:
                                if not(tx_input["address"] in self.shapeshift_stop_addresses):
                                    self.shapeshift_single_addresses.add(tx_input["address"])
                    else:
                        # Leave only Shapeshift Address in Outputs
                        exchange_transaction["outputs"] = [tx_output]

                        exchange_transaction["is_exchange_deposit"] = True
                        exchange_transaction["is_exchange_withdrawl"] = False

                    # Delete single addresses after analysing transaction, because no more needed
                    for tx_output_delete in exchange_transaction["outputs"]:
                        if tx_output_delete["address"] in self.shapeshift_single_addresses:
                            self.shapeshift_single_addresses.remove(tx_output_delete["address"])
                    return exchange_transaction
            # If nothing found in outputs, check if Shapeshift address in inputs
            for tx_input in exchange_transaction["inputs"]:
                if tx_input["address"] in self.shapeshift_stop_addresses:
                    exchange_transaction["is_exchange_deposit"] = False
                    exchange_transaction["is_exchange_withdrawl"] = True
                    for tx_input_add in exchange_transaction["inputs"]:
                        if not(tx_input_add["address"] in self.shapeshift_stop_addresses):
                            self.shapeshift_single_addresses.add(tx_input_add["address"])
                    return exchange_transaction
            return exchange_transaction

    def check_and_save_if_shapeshift_related_prepare(self, exchange_transaction):
        for tx_output in exchange_transaction["outputs"]:
            if tx_output["address"] in self.shapeshift_main_addresses \
                    or tx_output["address"] in self.shapeshift_middle_addresses \
                    or tx_output["address"] in self.shapeshift_single_addresses:
                print("Found match in Transaction: " + str(exchange_transaction["hash"]))
                if tx_output["address"][0] != "3" or tx_output["address"] in self.shapeshift_main_addresses:
                    # Check if input address was already used and move from single to middle class.
                    if len(exchange_transaction["inputs"]) == 1 and exchange_transaction["inputs"][0]["address"] in self.shapeshift_single_addresses:
                        print("Adding new MIDDLE Addresses: " + str(exchange_transaction["inputs"][0]["address"]))
                        self.shapeshift_single_addresses.remove(exchange_transaction["inputs"][0]["address"])
                        self.shapeshift_middle_addresses.add(exchange_transaction["inputs"][0]["address"])
                    else:
                        for tx_input in exchange_transaction["inputs"]:
                            if not(tx_input["address"] in self.shapeshift_stop_addresses):
                                print("Adding new SINGLE Address: " + str(tx_input["address"]))
                                self.shapeshift_single_addresses.add(tx_input["address"])
                for tx_output_delete in exchange_transaction["outputs"]:
                    if tx_output_delete["address"] in self.shapeshift_single_addresses:
                        print("Deleting SINGLE Address: " + str(tx_output["address"]))
                        self.shapeshift_single_addresses.remove(tx_output_delete["address"])
                return
        # If nothing found in outputs, check if Shapeshift address in inputs
        for tx_input in exchange_transaction["inputs"]:
            if tx_input["address"] in self.shapeshift_stop_addresses:
                exchange_transaction["is_exchange_deposit"] = False
                exchange_transaction["is_exchange_withdrawl"] = True
                for tx_input_add in exchange_transaction["inputs"]:
                    if not(tx_input_add["address"] in self.shapeshift_stop_addresses):
                        self.shapeshift_single_addresses.add(tx_input_add["address"])
                return

    # Iterates over the next x (number_of_blocks) blocks to generate a internal database of known Shapeshift Addresses
    def prepare_addresses(self, endblock_BTC):
        number_of_blocks = Settings.get_preparation_range("BTC")
        start_block = endblock_BTC + number_of_blocks
        for number in range(number_of_blocks):
            current_number = start_block - number
            print("Check block:" + str(current_number))
            new_transactions = Currency_apis.get_block_by_number("BTC", current_number)
            print("Number of txs: " + str(len(new_transactions)))
            for transaction in new_transactions:
                self.check_and_save_if_shapeshift_related_prepare(transaction)
            print("Number of single addresses: " + str(len(self. shapeshift_single_addresses)))
        # Optional. Save all found adresses
        for address in self.shapeshift_middle_addresses:
            Database_manager.insert_shapeshift_address_btc(address, "middle")
        for address in self.shapeshift_single_addresses:
            Database_manager.insert_shapeshift_address_btc(address, "single")

    def filter_block(self, new_transactions):
        block = []
        for new_transaction in new_transactions:
            transaction = self.check_and_save_if_shapeshift_related(new_transaction)
            if new_transaction["is_exchange_deposit"] or new_transaction["is_exchange_withdrawl"]:
                block.append(transaction)
        return block

def main():
    start_time = time.time()
    Database_manager.initialize_db()
    Database_manager.create_table_shapeshift_addresses_btc()
    address_tracker = Address_tracker_btc()
    address_tracker.prepare_addresses(511557)

    print("Duration: " + str(time.time() - start_time))
    print("finish")


if __name__ == "__main__": main()