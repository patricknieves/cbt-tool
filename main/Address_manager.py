from Address_tracker_eth import Address_tracker_eth


class Address_manager(object):
    def __init__(self, current_block_number_dict):
        self.address_tracker_eth = Address_tracker_eth(current_block_number_dict["ETH"])

    def is_exchange_deposit(self, exchange_transaction):
        if exchange_transaction["symbol"] == "ETH":
            if self.address_tracker_eth.is_shapeshift_related_as_deposit(exchange_transaction):
                return True
        elif exchange_transaction["symbol"] == "BTC":
            # TODO if BTC: for new_transaction in new_transactions: Address_tracker_btc.check_if_shapeshift_related(new_transaction)
            return True
        elif exchange_transaction["symbol"] == "LTC":
            # TODO implement Address recognition for LTC
            return True
        return False

    def is_exchange_withdrawl(self, exchange_transaction):
        if exchange_transaction["symbol"] == "ETH":
            if self.address_tracker_eth.is_shapeshift_related_as_withdrawl(exchange_transaction):
                return True
        elif exchange_transaction["symbol"] == "BTC":
            # TODO if BTC: for new_transaction in new_transactions: Address_tracker_btc.check_if_shapeshift_related(new_transaction)
            return True
        elif exchange_transaction["symbol"] == "LTC":
            # TODO implement Address recognition for LTC
            return True
        return False
