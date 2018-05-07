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

def get_trading_platform_addresses():
    return ["1N52wHoVR79PMDishab2XmRHsbekCdGquK", #Bittrex
             "14cQRmViAzVKa277gZznByGZtnrVPQc8Lr", # Bittrex
             "1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g", #Bitfinex
             "12cgpFdJViXbwHbhrA3TuW1EGnL25Zqc3P", #Poloniex
             "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s", #Binance
             "1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7" # Shapeshifts main Address
             ]

def get_hashes_to_block():
    """ Bitcoin addresses containin unknown inputs and will be blocked """
    return ["41a5261ae9c3e96380843b92a5987e54f2c221d85806d5ddecc3bef9b466ccaa",
              "95e3a55763e7e6be4b95b4e7d695db86760ae9d5b31a13d570f45b2b276da5f9",
              "e98f95d7171bddf544f56e99f9fed92c94cec8d623a7186d66cae475a3f8af16",
              "da1c14838143709b5ba961c4db68febfb63f1eac07557242959b097b8e8abf7e",
              "9587a71ca48ffc64159bca1d57e6acbf3d87ac6787bef42dae6532154f04c50b",
              "32d52344583cc8d7d0bf27d5617160a0fdccefabe2daa0f63760ee527d7995ce",
              "34a0eea9fe2e2164706fa0b67c7ebaa019d6839dc1a2289aa47701ec32c445e2",
              "32d52344583cc8d7d0bf27d5617160a0fdccefabe2daa0f63760ee527d7995ce",
              "d2ebe488bf3ee01023fe12aa611a21cfa22aacb674373a176e2cd5df38d035a8",
              "db8d8406284a64c0bbcfa2f4488c7d3c5b7e51bbdd7b0066ef424898dcff1f56",
              "b64fe139fe0635591b5309c4ecbd235311ea86b253c30a985fb376f571267c4a",
              "f413f5867238a55e62599852958d328808915fcaf70644ef86cd02e19bd7ab82",
              "9f6dafd7e2c8db6052752a0b691a86f5d9fbc5f42db7c17774ad1feb3c16be1b",
              "10967b4229656b3b8c16b7363d91712c377b7ecb28b8396b1f1084adcfedf63d",
              "b02580732ce7a6a3a00c4b8a816f7470f924e223cc01122ce6af0e60615b8e38",
              "2ebed81cc9a91f6710d230ed2a542281e5ccdae676cad811d69a0819804cfc7d",
              "1b3bdc17763b2c38937eacfbb384d20505ca1dc0f575a6f09df841ad9ac5e57f",
              "1c59264c95d3322912848625243ce08ec1a09b1ca99544ae4276304a509411b7",
              "35ff6eb26adf0d2f5bd00c14079e28d0d9d0bf7254c25c166c7f8221032fd386",
              "413424b741775e4e33f49fc3067360fec57fa9b9c276a27220e21b09a170143a",
              "9e25ea4e4a57d9b9f73299ea813bd50da4beb6908e5ad89771db02fcb2d5841c",
              "5ce5853240822ec07fdc005d6ec3e881036f96bea89802260a870802dbdfc201",
              "9f64a4d7afe68b5cc5a4d4fed12b2d016132313b24e16cf30cf34beae1b100a2",
              "bab46b129cd3730d5a5f0c441d630256966b379d6e2718caacbf4dcbc8710904",
              "712e1862b8841a7443e0f321b1b8b6cd677d0d21add2ca4d83a6ba0f8e819918",
              "bee9980bba165227ba4c676fe464fbdd7945b99f467aeb34a728f3586bd7b33b"]