def get_rate_lower_bound(currency):
    if currency == "BTC":
        return 0.70
    elif currency == "ETH":
        return 0.90
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