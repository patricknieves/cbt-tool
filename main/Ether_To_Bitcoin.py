from __future__ import division
import datetime
import Database_manager
from Currency_data import Currency_data
import Currency_apis
import Shapeshift

# TODO change all API Requests with full node Requests

current_block_number_BTC = Currency_apis.get_last_block_number_BTC()
transactions_BTC = []

def find_exchanges():
    currency_data_BTC = Currency_data("BTC", "USD")
    currency_data_ETH = Currency_data("ETH", "USD")

    # Get starting point for ETH
    last_block_number_ETH = Currency_apis.get_last_block_number_ETH()

    # TODO change to while loop
    for number in range(100):
        transactions_ETH = Currency_apis.get_last_block_by_number_ETH(last_block_number_ETH - number)
        for transaction_ETH in transactions_ETH:
            transaction_time_ETH = datetime.datetime.strptime(transaction_ETH["time"].replace("T"," ")[:-5], "%Y-%m-%d %H:%M:%S")
            transactions_BTC = load_txs_BTC(transaction_time_ETH)
            output = transaction_ETH["amount"]/1E+18
            for transaction_BTC in transactions_BTC:
                transaction_time_BTC = datetime.datetime.utcfromtimestamp(transaction_BTC["time"])
                # Searching for corresponding transaction not older than 5 min
                if (transaction_time_ETH - transaction_time_BTC).total_seconds() < 300:
                    # But older than 1 min
                    if (transaction_time_ETH - transaction_time_BTC).total_seconds() < 60:
                        transactions_BTC.remove(transaction_BTC)
                    else:
                        # Get Rate from CMC for certain block time. (Block creation time (input Currency) is used for both)
                        dollarvalue_from = currency_data_BTC.get_value(transaction_BTC["blocktime"])
                        dollarvalue_to = currency_data_ETH.get_value(transaction_BTC["blocktime"])
                        rate_cmc = dollarvalue_from/dollarvalue_to
                        # Compare Values with Rates
                        for output_BTC in transaction_BTC["out"]:
                            input = output_BTC["value"]/100000000
                            expected_output = input * rate_cmc
                            if output < expected_output and output > expected_output * 0.9:
                                fee_from = Currency_apis.get_fee_BTC(transaction_BTC["hash"])
                                fee_to = (transaction_ETH["gasUsed"]*(transaction_ETH["price"]/ 1E+18))
                                address_from = output_BTC["addr"]
                                address_to = transaction_ETH["recipient"]
                                hash_from = transaction_BTC["hash"]
                                hash_to = transaction_ETH["hash"]
                                exchanger = Shapeshift.get_exchanger(address_from, "ETH")
                                # Update DB
                                Database_manager.insert_exchange("BTC",
                                                                 "ETH",
                                                                 input,
                                                                 output,
                                                                 fee_from,
                                                                 fee_to,
                                                                 (expected_output - output), #Is this true?
                                                                 address_from,
                                                                 address_to,
                                                                 hash_from,
                                                                 hash_to,
                                                                 transaction_time_BTC.strftime('%Y-%m-%d %H:%M:%S'),
                                                                 transaction_time_ETH.strftime('%Y-%m-%d %H:%M:%S'),
                                                                 dollarvalue_from,
                                                                 dollarvalue_to,
                                                                 exchanger
                                                                 )
                                transactions_BTC.remove(transaction_BTC)
                                break
                else:
                    print("Exchange not found for this Ethereum Transaction: " + str(transaction_ETH["hash"]))
                    break

def load_txs_BTC(transaction_time_ETH):
    global current_block_number_BTC
    global transactions_BTC

    # Check if BTC Array long enough. If not load more blocks until time difference of 10 min is reached
    while (transaction_time_ETH - time_block_last).total_seconds() < 600:
        # Load new BTC transactions
        current_block_number_BTC = current_block_number_BTC - 1
        block = Currency_apis.get_block_by_number_BTC(current_block_number_BTC)
        for transaction in block["tx"]:
            transaction["blocktime"] = block["time"]
        transactions_BTC.extend(block["tx"])
        time_block_last = datetime.datetime.utcfromtimestamp(block["time"])
    # Sort BTC List
    transactions_BTC.sort(key=lambda x: datetime.datetime.utcfromtimestamp(x["time"]), reverse=True)
    return transactions_BTC
