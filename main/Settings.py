def get_rate_lower_bound(currency):
    if currency == "BTC":
        return 0.55
    elif currency == "ETH":
        return 0.80
    elif currency == "LTC":
        return 0.90
    else:
        return 0.95


def get_rate_upper_bound(currency):
    if currency == "BTC":
        return 1.02
    elif currency == "ETH":
        return 1.02
    elif currency == "LTC":
        return 1.02
    else:
        return 1.02


def get_exchange_time_lower_bound(currency):
    if currency == "BTC":
        return 0.5*60
    elif currency == "ETH":
        return 0.5*60
    elif currency == "LTC":
        return 0.5*60
    else:
        return 0.5*60


def get_exchange_time_upper_bound(currency):
    if currency == "BTC":
        return 5*60
    elif currency == "ETH":
        return 5*60
    elif currency == "LTC":
        return 13*60
    else:
        return 5*60

def get_preparation_range(currency):
    if currency == "BTC":
        return 506
    elif currency == "ETH":
        return 1000
    else:
        return

def get_exchanger_fee(currency):
    if currency == "BTC":
        return 0.00175
    elif currency == "ETH":
        return 0.01
    else:
        return

def get_scraper_offset(currency):
    if currency == "BTC":
        return 0
    elif currency == "ETH":
        return 15
    else:
        return

def get_scraper_offset_last_block(currency):
    if currency == "BTC":
        return 6
    elif currency == "ETH":
        return 40
    else:
        return