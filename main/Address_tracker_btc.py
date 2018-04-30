import Database_manager
import Currency_apis
import Settings
import time
from async_requests import Async_requester


class Address_tracker_btc(object):
    def __init__(self):
        #self.shapeshift_main_addresses = set(Database_manager.get_all_shapeshift_addresses_btc())
        self.shapeshift_main_addresses = Settings.get_main_addresses()

        #self. shapeshift_middle_addresses = set([])
        #self. shapeshift_single_addresses = set([])

        self.shapeshift_middle_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("middle")
        self.shapeshift_single_addresses = Database_manager.get_all_shapeshift_middle_addresses_btc("single")
        #self.shapeshift_stop_addresses = ["1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7"]
        self.shapeshift_trader_addresses = ["1N52wHoVR79PMDishab2XmRHsbekCdGquK",
                                            "14cQRmViAzVKa277gZznByGZtnrVPQc8Lr",
                                            "1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g",
                                            "12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P",
                                            "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
                                            "1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7"
                                            ]

    def recognize_and_categorize(self, exchange_transaction):
        for tx_output in exchange_transaction["outputs"]:
            if tx_output["address"] in self.shapeshift_main_addresses \
                    or tx_output["address"] in self.shapeshift_middle_addresses \
                    or tx_output["address"] in self.shapeshift_single_addresses:

                #Check if input from trading platform. If yes, ignore tx
                ignore = False
                for tx_input in exchange_transaction["inputs"]:
                    if tx_input["address"] in self.shapeshift_trader_addresses:
                        ignore = True
                        break
                if ignore:
                    return exchange_transaction

                if tx_output["address"][0] != "3" or tx_output["address"] in self.shapeshift_main_addresses:
                    # Delete Shapeshift Address from Outputs (and leave only User Address(es))
                    exchange_transaction["outputs"].remove(tx_output)

                    exchange_transaction["is_exchange_deposit"] = False
                    exchange_transaction["is_exchange_withdrawl"] = True

                    for tx_input in exchange_transaction["inputs"]:
                        #if not(tx_input["address"] in self.shapeshift_stop_addresses) \
                        if not(tx_input["address"] in self.shapeshift_main_addresses) \
                                and not(tx_input["address"] in self.shapeshift_middle_addresses):
                            # Check if input address was already used and move from single to middle class. (len(exchange_transaction["inputs"]) == 1 and)
                            if tx_input["address"] in self.shapeshift_single_addresses:
                                self.shapeshift_single_addresses.remove(tx_input["address"])
                                self.shapeshift_middle_addresses.add(tx_input["address"])
                            else:
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
        return exchange_transaction

    def recognize(self, exchange_transaction):
        for tx_output in exchange_transaction["outputs"]:
            if tx_output["address"] in self.shapeshift_main_addresses \
                    or tx_output["address"] in self.shapeshift_middle_addresses \
                    or tx_output["address"] in self.shapeshift_single_addresses:
                print("Found match in Transaction: " + str(exchange_transaction["hash"]))

                #Check if input from trading platform. If yes, ignore tx
                ignore = False
                for tx_input in exchange_transaction["inputs"]:
                    if tx_input["address"] in self.shapeshift_trader_addresses:
                        ignore = True
                        break
                if ignore:
                    return exchange_transaction

                if tx_output["address"][0] != "3" or tx_output["address"] in self.shapeshift_main_addresses:

                    for tx_input in exchange_transaction["inputs"]:
                        #if not(tx_input["address"] in self.shapeshift_stop_addresses) \
                        if not(tx_input["address"] in self.shapeshift_main_addresses)\
                                and not(tx_input["address"] in self.shapeshift_middle_addresses):
                            # Check if input address was already used and move from single to middle class. (len(exchange_transaction["inputs"]) == 1 and)
                            if tx_input["address"] in self.shapeshift_single_addresses:
                                print("Adding new MIDDLE Addresses: " + str(tx_input["address"]))
                                self.shapeshift_single_addresses.remove(tx_input["address"])
                                self.shapeshift_middle_addresses.add(tx_input["address"])
                            else:
                                print("Adding new SINGLE Address: " + str(tx_input["address"]))
                                self.shapeshift_single_addresses.add(tx_input["address"])

                for tx_output_delete in exchange_transaction["outputs"]:
                    if tx_output_delete["address"] in self.shapeshift_single_addresses:
                        print("Deleting SINGLE Address: " + str(tx_output["address"]))
                        self.shapeshift_single_addresses.remove(tx_output_delete["address"])
                return

    def prepare_addresses(self, current_block_nr):
        nr_of_async_blocks = 10
        async_requester = Async_requester()
        number_of_blocks = Settings.get_preparation_range("BTC")
        start_block = current_block_nr + number_of_blocks
        current_number = start_block
        while current_number > current_block_nr:
            print("Check " + str(nr_of_async_blocks) + " blocks from:" + str(current_number))
            if (current_number - current_block_nr) > nr_of_async_blocks:
                async_requester.add_request_data("BTC", current_number, nr_of_async_blocks)
            else:
                async_requester.add_request_data("BTC", current_number, current_number - current_block_nr)
            new_blocks = async_requester.get_multiple_blocks()
            current_number = current_number - nr_of_async_blocks
            for new_transactions in new_blocks:
                for transaction in new_transactions:
                    self.recognize(transaction)
            print("Number of single addresses: " + str(len(self. shapeshift_single_addresses)))
        # Optional. Save all found adresses
        for address in self.shapeshift_middle_addresses:
            Database_manager.insert_shapeshift_address_btc(address, "middle")
        for address in self.shapeshift_single_addresses:
            Database_manager.insert_shapeshift_address_btc(address, "single")

    def filter_block(self, new_transactions):
        block = []
        for new_transaction in new_transactions:
            transaction = self.recognize_and_categorize(new_transaction)
            if new_transaction["is_exchange_deposit"] or new_transaction["is_exchange_withdrawl"]:
                block.append(transaction)
        return block

    def save_all_addresses(self):
        Database_manager.create_table_shapeshift_addresses_btc_end()
        for address in self.shapeshift_middle_addresses:
            Database_manager.insert_shapeshift_address_btc_end(address, "middle")
        for address in self.shapeshift_single_addresses:
            Database_manager.insert_shapeshift_address_btc_end(address, "single")

def main():
    start_time = time.time()
    Database_manager.initialize_db()
    Database_manager.create_table_shapeshift_addresses_btc()
    address_tracker = Address_tracker_btc()
    address_tracker.prepare_addresses(511557)

    print("Duration: " + str(time.time() - start_time))
    print("finish")


if __name__ == "__main__": main()