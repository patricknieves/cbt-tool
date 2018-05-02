import time
from main import Shapeshift_api


class Shapeshift_fee(object):
    """ Class responible for scraping the Shapeshift fee """

    def __init__(self):
        self.shapeshift_fee_data = Shapeshift_api.get_fees_shapeshift()
        self.last_update_time = time.time()

    def get_shapeshift_fee(self, currency):
        """ Returns the Shapeshift fee for a given currency
         and updates the Shapeshift fees for all currencies every 30 minutes """
        current_time = time.time()
        # Update data every 30 min
        if (current_time - self.last_update_time) > 30*60:
            fees = Shapeshift_api.get_fees_shapeshift()
            if fees:
                self.shapeshift_fee_data = fees
            self.last_update_time = current_time
        for exchange in self.shapeshift_fee_data:
            currency_shapeshift = exchange["pair"].split('_')[1]
            if currency_shapeshift == currency:
                return exchange["minerFee"]