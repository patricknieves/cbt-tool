from __future__ import division

import datetime
import sys
import time
import traceback

import requests

import Tor


def get_last_block_number(currency):
    """ Gets the most recent block number for the given currency """
    Tor.change_ip()
    for attempt in range(10):
        try:
            if currency == "BTC":
                last_block_number = requests.get("https://blockchain.info/de/latestblock").json()["height"]
            elif currency == "ETH":
                last_block_number = int(requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_blockNumber?token=Wh9YuEIhi7tqseXn8550").json()["result"], 16)
            elif currency == "LTC":
                last_block_number = requests.get("https://chain.so/api/v2/get_info/LTC").json()["data"]["blocks"]
            else:
                print ("Couldn't get last number of block. Not such a currency: " + currency)
                return
        except:
            print ("Wait a minute. Loading block number for " + currency)
            time.sleep(60)
            Tor.change_ip()
        else:
            return last_block_number
    else:
        traceback.print_exc()
        sys.exit("Couldn't get last number of block for " + currency)


def get_block_by_number(currency, number):
    """ Gets a block with the given block number for a given currency """
    Tor.change_ip()
    for attempt in range(5):
        try:
            if currency == "BTC":
                block = requests.get("https://blockchain.info/de/block-height/" + (str(number)) + "?format=json").json()["blocks"][0]
                block["tx"].sort(key=lambda x: datetime.datetime.utcfromtimestamp(x["time"]), reverse=True)
            elif currency == "ETH":
                block = requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_getBlockByNumber?params=%5B%22" + hex(number) + "%22%2C%20true%5D&token=Wh9YuEIhi7tqseXn8550").json()["result"]
            elif currency == "LTC":
                block = requests.get("https://chain.so/api/v2/block/LTC/" + (str(number))).json()["data"]
            else:
                print ("Couldn't get block. Not such a currency: " + currency)
                return
        except:
            print ("Wait a minute. Loading block for " + currency)
            time.sleep(60)
            Tor.change_ip()
        else:
            return standardize(currency, block)
    else:
        traceback.print_exc()
        sys.exit("Counldn't get block for " + currency + ": " + str(number))


def standardize(currency, json):
    """ Converts the returned block data from external APIs into a standardized dictionary """
    standardized_dict = []
    if currency == "BTC":
        for transaction in json["tx"]:
            dict_item = {"symbol": currency,
                         "time": datetime.datetime.utcfromtimestamp(transaction["time"]),
                         "blocktime": datetime.datetime.utcfromtimestamp(json["time"]),
                         "fee": None,
                         "hash": transaction["hash"],
                         "block_nr": json["height"],
                         "inputs": [],
                         "outputs": [],
                         "is_exchange_deposit": None,
                         "is_exchange_withdrawl": None
                         }
            # Get inputs and outputs & calculate fee
            input_value = 0
            output_value = 0
            for tx_input in transaction["inputs"]:
                if "prev_out" in tx_input and tx_input["prev_out"]["value"] != 0 and "addr" in tx_input["prev_out"]:
                    dict_item_input = {"amount": tx_input["prev_out"]["value"] / 100000000,
                                       "address": tx_input["prev_out"]["addr"]}
                    dict_item["inputs"].append(dict_item_input)
                    input_value = input_value + tx_input["prev_out"]["value"] / 100000000
            for tx_output in transaction["out"]:
                if tx_output["value"] != 0 and "addr" in tx_output:
                    dict_item_output = {"amount": tx_output["value"] / 100000000,
                                        "address": tx_output["addr"]}
                    dict_item["outputs"].append(dict_item_output)
                    output_value = output_value + tx_output["value"] / 100000000
            # If input_value == 0 it is a coinbase tx and there are no fees
            if input_value != 0:
                dict_item["fee"] = input_value - output_value
            standardized_dict.append(dict_item)

    elif currency == "ETH":
        for transaction in json["transactions"]:
            if int(transaction["value"], 16) / 1E+18 != 0:
                dict_item = {"symbol": currency, "amount": int(transaction["value"], 16) / 1E+18,
                             "time": datetime.datetime.utcfromtimestamp(int(json["timestamp"], 16)), # same as block time/ tx time not provided
                             "blocktime": datetime.datetime.utcfromtimestamp(int(json["timestamp"], 16)),
                             "fee": (int(transaction["gas"], 16) * int(transaction["gasPrice"], 16)) / 1E+18, # This is gas provided, but not real gas spent
                             "hash": transaction["hash"], "block_nr": int(json["number"], 16),
                             "inputs": [],
                             "outputs": [],
                             "is_exchange_deposit": None,
                             "is_exchange_withdrawl": None}
                dict_item_input = {"amount": int(transaction["value"], 16) / 1E+18,
                                   "address": transaction["from"]}
                dict_item["inputs"] = [dict_item_input]
                dict_item_output = {"amount": int(transaction["value"], 16) / 1E+18,
                                    "address": transaction["to"]}
                dict_item["outputs"] = [dict_item_output]
                standardized_dict.append(dict_item)

    elif currency == "LTC":
        for transaction in json["txs"]:
            dict_item = {"symbol": currency,
                         "time": datetime.datetime.utcfromtimestamp(json["time"]), # same as block time/ tx time not provided
                         "blocktime": datetime.datetime.utcfromtimestamp(json["time"]),
                         "fee": transaction["fee"],
                         "hash": transaction["txid"],
                         "block_nr": json["block_no"],
                         "is_exchange_deposit": None,
                         "is_exchange_withdrawl": None}
            for tx_input in transaction["inputs"]:
                if float(tx_input["value"]) != 0:
                    dict_item_input = {"amount": float(tx_input["value"]),
                                       "address": tx_input["address"]}
                    dict_item["inputs"].append(dict_item_input)
            for tx_output in transaction["out"]:
                if float(tx_output["value"]) != 0:
                    dict_item_output = {"amount": float(tx_output["value"]),
                                        "address": tx_output["address"]}
                    dict_item["outputs"].append(dict_item_output)
            standardized_dict.append(dict_item)

    else:
        print ("Couldn't standardize block for " + currency)
        return
    return standardized_dict


def get_transactions_for_address(currency, address):
    """ Returns all transactions involving a given address for a given currency """
    Tor.change_ip()
    transactions = None
    for attempt in range(5):
        try:
            if currency == "ETH":
                transactions = requests.get("http://api.etherscan.io/api?module=account&"
                                            "action=txlist&" +
                                            "address=" + address +
                                            "&sort=desc" +
                                            "&apikey=" + "2BBQWBUF94KBKWQMASY3PBCGF7737FTK5N").json()["result"]
            elif currency == "BTC":
                transactions = requests.get("https://blockchain.info/de/rawaddr/" + address).json()["txs"]
        except:
            print ("Wait 5 sec")
            time.sleep(5)
            Tor.change_ip()
        else:
            return transactions
    else:
        traceback.print_exc()
        print("Couldn't get transactions from Etherscan")
