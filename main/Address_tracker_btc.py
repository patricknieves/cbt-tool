import Database_manager


class Address_tracker_btc(object):
    def __init__(self):
        self.shapeshift_main_addresses = set(Database_manager.get_all_shapeshift_addresses_btc())
        self. shapeshift_middle_addresses = set([])
        self. shapeshift_single_addresses = set([])

    def check_and_save_if_shapeshift_related(self, exchange_transaction):
            for tx_output in exchange_transaction["outputs"]:
                if (tx_output["address"] in self.shapeshift_main_addresses and len(exchange_transaction["inputs"]) > 8) \
                        or tx_output["address"] in self.shapeshift_middle_addresses \
                        or tx_output["address"] in self.shapeshift_single_addresses:
                    print("SS Tx found!")
                    if tx_output["address"][0] != "3":
                        # Check if input address was already used and move from single to middle class.
                        if len(exchange_transaction["inputs"]) == 1 and exchange_transaction["inputs"][0]["address"] in self.shapeshift_single_addresses:
                            self.shapeshift_single_addresses.remove(exchange_transaction["inputs"][0]["address"])
                            self.shapeshift_middle_addresses.add(exchange_transaction["inputs"][0]["address"])
                        else:
                            print("Adding new Addresses: " + str(len(exchange_transaction["inputs"])))
                            for tx_input in exchange_transaction["inputs"]:
                                self.shapeshift_single_addresses.add(tx_input["address"])
                            # Delete single addresses after analysing transaction, because no more needed
                            #if tx_output["address"] in self.shapeshift_single_addresses:
                            #    self.shapeshift_single_addresses.remove(tx_output["address"])
                    return True
            return False

    def is_shapeshift_related_as_deposit(self, exchange_transaction):
        for tx_output in exchange_transaction["outputs"]:
            if tx_output["address"][0] == "3" and tx_output["address"] in self.shapeshift_single_addresses:
                return True
        return False