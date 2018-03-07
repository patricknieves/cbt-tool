import Database_manager
import Currency_apis
import Settings


class Address_tracker_btc(object):
    def __init__(self, current_block_number):
        self.endblock_BTC = current_block_number
        #self.shapeshift_main_addresses = set(Database_manager.get_all_shapeshift_addresses_btc())
        self.shapeshift_main_addresses = ["1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG",
                                     "1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk",
                                     "1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM",
                                     "1jhbBbDRdezEZ5tSsHZwuUg85Hhf4rWuz",
                                     "3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B"]
        #self. shapeshift_middle_addresses = set([])
        #self. shapeshift_single_addresses = set([])
        self. shapeshift_middle_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("middle")
        self. shapeshift_single_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("single")
        self.shapeshift_stop_addresses = ["1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7"]

    def check_and_save_if_shapeshift_related(self, exchange_transaction):
            for tx_output in exchange_transaction["outputs"]:
                if (tx_output["address"] in self.shapeshift_main_addresses and len(exchange_transaction["inputs"]) > 3 and not(all(tx_input["address"][0] == "1" for tx_input in exchange_transaction["inputs"]))) \
                        or tx_output["address"] in self.shapeshift_middle_addresses \
                        or tx_output["address"] in self.shapeshift_single_addresses:
                    if tx_output["address"][0] != "3":
                        # Delete Shapeshift Address from Outputs (and leave only User Address)
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
                    if tx_output["address"] in self.shapeshift_single_addresses:
                        self.shapeshift_single_addresses.remove(tx_output["address"])
                    break
            return exchange_transaction

    def check_and_save_if_shapeshift_related_prepare(self, exchange_transaction):
        for tx_output in exchange_transaction["outputs"]:
            if (tx_output["address"] in self.shapeshift_main_addresses and len(exchange_transaction["inputs"]) > 3 and not(all(tx_input["address"][0] == "1" for tx_input in exchange_transaction["inputs"]))) \
                    or tx_output["address"] in self.shapeshift_middle_addresses \
                    or tx_output["address"] in self.shapeshift_single_addresses:
                print("Found match in Transaction: " + str(exchange_transaction["hash"]   ))
                if tx_output["address"][0] != "3":
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
                # Delete single addresses after analysing transaction, because no more needed
                if tx_output["address"] in self.shapeshift_single_addresses:
                    print("Deleting SINGLE Address: " + str(tx_output["address"]))
                    self.shapeshift_single_addresses.remove(tx_output["address"])
                break

    # Iterates over the next x (number_of_blocks) blocks to generate a internal database of known Shapeshift Addresses
    def prepare_addresses(self):
        number_of_blocks = Settings.get_preparation_range("BTC")
        start_block = self.endblock_BTC + number_of_blocks
        for number in range(number_of_blocks):
            print("Check block:" + str(start_block - number))
            new_transactions = Currency_apis.get_block_by_number("BTC", start_block - number)
            for transaction in new_transactions:
                self.check_and_save_if_shapeshift_related_prepare(transaction)
        # Optional. Save all found adresses
        for address in self.shapeshift_main_addresses:
            Database_manager.insert_shapeshift_address_btc(address, "main")
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