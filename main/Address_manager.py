from Address_tracker_eth import Address_tracker_eth
from Address_tracker_btc import Address_tracker_btc
from async_requests import Async_requester


class Address_manager(object):
    def __init__(self, current_block_number_dict):
        self.address_tracker_eth = Address_tracker_eth(current_block_number_dict["ETH"])
        self.address_tracker_btc = Address_tracker_btc(current_block_number_dict["BTC"])
        #self.async_requester = Async_requester()

    def is_exchange_deposit(self, exchange_transaction):
        return exchange_transaction["is_exchange_deposit"]

    def is_exchange_withdrawl(self, exchange_transaction):
        return exchange_transaction["is_exchange_withdrawl"]

    def prepare(self):
        self.address_tracker_btc.prepare_addresses()
        # TODO maybe also prepare for ETH: get a range of Shapeshift Addresses

    def filter_block(self, block):
        if block:
            currency = block[0]["symbol"]
            if currency == "BTC":
                return self.address_tracker_btc.filter_block(block)
            elif currency == "ETH":
                return self.address_tracker_eth.filter_block(block)
        return []

    def get_block_by_number(self, currency, current_block_number):
        if currency == "BTC":
            return self.address_tracker_btc.get_block_by_number_only_shapeshift_txs(current_block_number)
        elif currency == "ETH":
            return self.address_tracker_eth.get_block_by_number_only_shapeshift_txs(current_block_number)
        else:
            return []

    # def get_blocks_by_number(self, currency, current_block_number, number_of_blocks):
    #     if currency == "BTC":
    #         blocks = self.async_requester.get_multiple_blocks(currency, current_block_number, number_of_blocks)
    #         return self.address_tracker_btc.get_blocks_by_number_only_shapeshift_txs(blocks)
    #     elif currency == "ETH":
    #         blocks = self.async_requester.get_multiple_blocks(currency, current_block_number, number_of_blocks)
    #         return self.address_tracker_eth.get_blocks_by_number_only_shapeshift_txs(blocks)
    #     else:
    #         return []
