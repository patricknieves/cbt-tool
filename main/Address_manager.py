from Address_tracker_eth import Address_tracker_eth
from Address_tracker_btc import Address_tracker_btc
from async_requests import Async_requester


class Address_manager(object):
    def __init__(self, current_block_number_dict):
        self.address_tracker_eth = Address_tracker_eth(current_block_number_dict["ETH"])
        self.address_tracker_btc = Address_tracker_btc(current_block_number_dict["BTC"])

    def prepare(self):
        #self.address_tracker_btc.prepare_addresses()
        self.address_tracker_eth.prepare_addresses()

    def filter_block_and_save_addresses(self, block):
        if block:
            currency = block[0]["symbol"]
            if currency == "BTC":
                return self.address_tracker_btc.filter_block(block)
            elif currency == "ETH":
                return self.address_tracker_eth.filter_block(block)
        return []
