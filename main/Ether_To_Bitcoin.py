from __future__ import division
import datetime
import Database_manager
from Currency_data import Currency_data
import Currency_apis
import Shapeshift

# TODO change all API Requests with full node Requests

currency_from = "ETH"
currency_to = "BTC"

current_block_number_from = Currency_apis.get_last_block_number(currency_from)
transactions_from = []


def find_exchanges():
    currency_data_from = Currency_data(currency_from, "USD")
    currency_data_to = Currency_data(currency_to, "USD")

    last_block_number_to = Currency_apis.get_last_block_number(currency_to)

    # TODO change to while loop
    for number in range(100):
        block_to = Currency_apis.get_block_by_number(currency_to, last_block_number_to - number)
        transactions_to = block_to["tx"]
        # TODO cut to 10/15 min?

        # Delete txs which are older than x min
        block_time_to = datetime.datetime.utcfromtimestamp(block_to["time"])
        for transaction_from in transactions_from:
            transaction_time_from = datetime.datetime.utcfromtimestamp(transaction_from["time"])
            if (block_time_to - transaction_time_from).total_seconds() < 60:
                transactions_from.remove(transaction_from)
            else:
                break

        for transaction_to in transactions_to:
            transaction_time_to = datetime.datetime.utcfromtimestamp(transaction_to["time"])
            transactions_from = load_txs_from(transaction_time_to)

            for output_BTC in transaction_to["out"]:
                output = output_BTC["value"]/100000000

                for transaction_from in transactions_from:
                    transaction_time_from = datetime.datetime.strptime(transaction_from["time"].replace("T"," ")[:-5], "%Y-%m-%d %H:%M:%S")
                    # Searching for corresponding transaction not older than 5 min
                    if (transaction_time_to - transaction_time_from).total_seconds() < 300:

                        # Get Rate from CMC for certain block time. (Block creation time (input Currency) is used for both)
                        dollarvalue_from = currency_data_from.get_value(transaction_from["time"])
                        dollarvalue_to = currency_data_to.get_value(transaction_from["time"])
                        rate_cmc = dollarvalue_from/dollarvalue_to
                        # Compare Values with Rates

                        input = transaction_from["amount"]/1E+18
                        expected_output = input * rate_cmc
                        if output < expected_output and output > expected_output * 0.9:
                            fee_from = (transaction_from["gasUsed"]*(transaction_from["price"]/ 1E+18))
                            fee_to = Currency_apis.get_fee_BTC(transaction_to["hash"])
                            address_from = transaction_from["recipient"]
                            address_to = output_BTC["addr"]
                            hash_from = transaction_from["hash"]
                            hash_to = transaction_to["hash"]
                            exchanger = Shapeshift.get_exchanger(address_from, currency_to)
                            # Update DB
                            Database_manager.insert_exchange(currency_from,
                                                             currency_to,
                                                             input,
                                                             output,
                                                             fee_from,
                                                             fee_to,
                                                             (expected_output - output),
                                                             address_from,
                                                             address_to,
                                                             hash_from,
                                                             hash_to,
                                                             transaction_time_from.strftime('%Y-%m-%d %H:%M:%S'),
                                                             transaction_time_to.strftime('%Y-%m-%d %H:%M:%S'),
                                                             dollarvalue_from,
                                                             dollarvalue_to,
                                                             exchanger
                                                             )
                            transactions_from.remove(transaction_from)
                            break
                    else:
                        print("Exchange not found for this Transaction: " + str(transaction_to["hash"]))
                        break


def load_txs_from(transaction_time_to):
    global current_block_number_from
    global transactions_from
    global time_block_last

    # Check if BTC Array long enough. If not load more blocks until time difference of 10 min is reached
    while not time_block_last or (transaction_time_to - time_block_last).total_seconds() < 600:
        # Load new BTC transactions
        current_block_number_from = current_block_number_from - 1
        block = Currency_apis.get_block_by_number(currency_from, current_block_number_from)

        transactions_from.extend(block)
        time_block_last = datetime.datetime.utcfromtimestamp(block[0]["time"])

    return transactions_from
