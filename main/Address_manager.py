from Address_tracker_eth import Address_tracker_eth
from Address_tracker_btc import Address_tracker_btc
from async_requests import Async_requester


class Address_manager(object):
    """ Class responsible for handling the Address recognition classes for all currencies """
    def __init__(self):
        self.address_tracker_eth = Address_tracker_eth()
        self.address_tracker_btc = Address_tracker_btc()

    def prepare(self, current_block_numbers):
        """ Executes the preparation process for the Address recognition of all currencies  """
        self.address_tracker_eth.prepare_addresses(current_block_numbers["ETH"])
        self.address_tracker_btc.prepare_addresses(current_block_numbers["BTC"])

    def filter_block_and_save_addresses(self, block):
        """ Executes the recognition process for one block """
        if block:
            currency = block[0]["symbol"]
            if currency == "BTC":
                return self.address_tracker_btc.filter_block(block)
            elif currency == "ETH":
                return self.address_tracker_eth.filter_block(block)
        return []

    def save_addresses_end(self):
        """ Saves the current list of identified Bitcoin addresses to the DB """
        self.address_tracker_btc.save_all_addresses()

    def count_addresses(self):
        """ Prints the current number of Bitcoin addresses identified """
        return "BTC Adresses: MIDDLE " + str(len(self.address_tracker_btc.shapeshift_middle_addresses)) + " & SINGLE: " + str(len(self.address_tracker_btc.shapeshift_single_addresses))
