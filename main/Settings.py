def get_rate_lower_bound(currency):
    if currency == "BTC":
        return 0.90
    elif currency == "ETH":
        return 0.90
    else:
        return 0.90


def get_rate_upper_bound(currency):
    if currency == "BTC":
        return 1.1
    elif currency == "ETH":
        return 1.1
    else:
        return 1.1


def get_exchange_time_lower_bound(currency):
    if currency == "BTC":
        return 0
    elif currency == "ETH":
        return 0
    else:
        return 0


def get_exchange_time_upper_bound(currency):
    if currency == "BTC":
        return 15*60
    elif currency == "ETH":
        return 15*60
    else:
        return 15*60


def get_preparation_range(currency):
    if currency == "BTC":
        return 506
    elif currency == "ETH":
        return 2000
    else:
        return

def get_exchanger_fee(currency, transaction_fee, number_of_outputs):
    if currency == "BTC":
        if number_of_outputs < 3:
            return transaction_fee * 1.6
        else:
            return transaction_fee * 0.3
    elif currency == "ETH":
        return transaction_fee * 1.8
    else:
        return


def get_scraper_offset(currency):
    if currency == "BTC":
        return 3
    elif currency == "ETH":
        return 40
    else:
        return

def get_scraper_offset_last_block(currency):
    if currency == "BTC":
        return 6
    elif currency == "ETH":
        return 40
    else:
        return

def get_scraper_offset_for_first_iteration(currency):
    if currency == "BTC":
        return 30
    elif currency == "ETH":
        return 400
    else:
        return

def get_block_number_for_hour(currency):
    if currency == "BTC":
        return 6
    elif currency == "ETH":
        return 4*60
    else:
        return
