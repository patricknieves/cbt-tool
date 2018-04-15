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
        return 5000
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

def get_main_addresses_old():
    return [
        "1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG", #Bittrex
        "1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk", #Bitfinex
        "1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM", #Poloniex
        "17NqGW6HY3f2LY7wFkEDn9yXpq8LWMRMEQ", #Binance #new
        "3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B", #Storage Address

        "1E57TDxSju3AEecoUjjQKkbGWAitP12znn", #Unkonwn #feb #new
        "1jhbBbDRdezEZ5tSsHZwuUg85Hhf4rWuz", #Unknown

        "1HFyPNX9gEvGHNCR34hkiseTLj2MXmqYr7",
        "1BiX4SkXd97AvjvTbGN1V9ykTtYf9EVXN5",
        "3N1f4Hv4dmMkFCyvAqu3M4wcQQYNJvs232", #feb # connections:1
        "17JnGQUbpqosaFZ7P3ywHQj6G75kERBSXa", # connetions: 0
        "1BngmLiuiXbzSNpwQ9kEbMy1KZ6xj5Jxs4" #feb
        #"1By2vSBudu7fSt7aeAR5tJza6HiGUhVcdJ", #feb #not a SS address - unknown inputs
    ]

def get_main_addresses():
    return ['1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk',
            '1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG',
            '1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM',
            '17NqGW6HY3f2LY7wFkEDn9yXpq8LWMRMEQ',
            '3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B',

            #"1Fq1iUJf58Xyv6gFzmjnbqNMPwQ3uhmwjL", #Deposit address (connections:0)
            #"1BxQLt8EkLKEVgf9ifXEM2PQHz3sEdbVy8", #Deposit address (connections:0)
            #"1JiDzKGZc81eMWxDncXc6EyBuW4NsopAb ", #Deposit address (connections:0)

            "1GJkx984EHyR5dCPvVisE9Y7p18MKa1ixs", #Deposit address (connections:0)
            "1NE6snFBUQD2aExH8KZdzEbDiNCyANjfVg" #Deposit address (connections:0)
            ]