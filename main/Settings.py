import traceback

import sys


def get_rate_lower_bound(currency):
    """ Lower bound for allowed deviation of the withdrawal amount from the expected amount """
    if currency == "BTC":
        return 0.90
    elif currency == "ETH":
        return 0.90
    else:
        return 0.90


def get_rate_upper_bound(currency):
    """ Upper bound for allowed deviation of the withdrawal amount from the expected amount """
    if currency == "BTC":
        return 1.1
    elif currency == "ETH":
        return 1.1
    else:
        return 1.1


def get_exchange_time_lower_bound(currency):
    """ Lower bound for allowed difference between block confirmation time of the deposit and the transaction time of the withdrawal """
    if currency == "BTC":
        return 0
    elif currency == "ETH":
        return 0
    else:
        return 0


def get_exchange_time_upper_bound(currency):
    """ Upper bound for allowed difference between block confirmation time of the deposit and the transaction time of the withdrawal """
    if currency == "BTC":
        return 15*60
    elif currency == "ETH":
        return 15*60
    else:
        return 15*60


def get_preparation_range(currency):
    """ Number of blocks to check at the preparation process """
    if currency == "BTC":
        return 5000
    elif currency == "ETH":
        return 2000
    else:
        return


def get_exchanger_fee(currency, transaction_fee, number_of_outputs):
    """ Returns an estimation of the Shapeshift fee based on the transaction fee paid and the number of outputs """
    try:
        if currency == "BTC":
            if number_of_outputs < 3:
                return transaction_fee * 1.6
            else:
                return transaction_fee * 0.3
        elif currency == "ETH":
            return transaction_fee * 1.8
        else:
            return
    except:
        traceback.print_exc()
        sys.exit("Error in program. Aborting")

def get_scraper_offset(currency):
    """ Number of blocks to skip when starting a new search loop in the Data retriever """
    if currency == "BTC":
        return 3
    elif currency == "ETH":
        return 40
    else:
        return

def get_scraper_offset_last_block(currency):
    """ Number of blocks to check in a loop by the Data Retriever, although they were checked in the previous loop """
    if currency == "BTC":
        return 6
    elif currency == "ETH":
        return 40
    else:
        return

def get_scraper_offset_for_first_iteration(currency):
    """ Number of blocks to check by the Data Retriever in the first loop (as no limit is set yet) """
    if currency == "BTC":
        return 30
    elif currency == "ETH":
        return 400
    else:
        return

def get_block_number_for_hour(currency):
    """ Number of blocks confirmed in an hour """
    if currency == "BTC":
        return 6
    elif currency == "ETH":
        return 4*60
    else:
        return


def get_main_addresses():
    """ Main Addresses from which the Bitcoin address recognition starts """
    return ['1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk', #Bitfinex
            '1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG', #Bittrex
            '1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM', #Poloniex
            '17NqGW6HY3f2LY7wFkEDn9yXpq8LWMRMEQ', #Binance
            '3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B', #Storage Address

            '1NE6snFBUQD2aExH8KZdzEbDiNCyANjfVg', #Deposit Address
            '1GJkx984EHyR5dCPvVisE9Y7p18MKa1ixs' #Deposit Address
            ]