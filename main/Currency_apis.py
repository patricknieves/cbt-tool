from __future__ import division

import datetime
import sys
import time
import traceback

import requests

import Tor


def get_last_block_number(currency):
    Tor.change_ip()
    for attempt in range(10):
        try:
            if currency == "BTC":
                last_block_number = requests.get("https://blockchain.info/de/latestblock").json()["height"]
            elif currency == "ETH":
                #last_block_number = requests.get("https://etherchain.org/api/blocks/count").json()["data"][0]["count"]
                last_block_number = int(requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_blockNumber?token=Wh9YuEIhi7tqseXn8550").json()["result"], 16)
            elif currency == "LTC":
                last_block_number = requests.get("https://chain.so/api/v2/get_info/LTC").json()["data"]["blocks"]
                #last_block_number = requests.get("https://api.blockcypher.com/v1/ltc/main").json()["height"]
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
    Tor.change_ip()
    for attempt in range(5):
        try:
            if currency == "BTC":
                block = requests.get("https://blockchain.info/de/block-height/" + (str(number)) + "?format=json").json()["blocks"][0]
                block["tx"].sort(key=lambda x: datetime.datetime.utcfromtimestamp(x["time"]), reverse=True)
            elif currency == "ETH":
                #block = requests.get("https://etherchain.org/api/block/" + (str(number)) + "/tx").json()["data"]
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
                         "outputs": []}
            for input in transaction["inputs"]:
                if input["value"] != 0 and "prev_out" in input and "addr" in input["prev_out"]:
                    dict_item_input = {"amount": input["prev_out"]["value"] / 100000000,
                                       "address": input["prev_out"]["addr"]}
                    dict_item["inputs"].append(dict_item_input)
            for output in transaction["out"]:
                if output["value"] != 0 and "addr" in output:
                    dict_item_output = {"amount": output["value"] / 100000000,
                                        "address": output["addr"]}
                    dict_item["outputs"].append(dict_item_output)
            standardized_dict.append(dict_item)

    elif currency == "ETH":
        for transaction in json["transactions"]:
            if int(transaction["value"], 16) / 1E+18 != 0:
                dict_item = {"symbol": currency, "amount": int(transaction["value"], 16) / 1E+18,
                             "time": datetime.datetime.utcfromtimestamp(int(json["timestamp"], 16)),
                             "blocktime": datetime.datetime.utcfromtimestamp(int(json["timestamp"], 16)), # same as tx time
                             "fee": (int(transaction["gas"], 16) * int(transaction["gasPrice"], 16)) / 1E+18,
                             "hash": transaction["hash"], "block_nr": int(json["number"], 16),
                             "inputs": [],
                             "outputs": []}
                dict_item_input = {"amount": int(transaction["value"], 16) / 1E+18,
                                   "address": transaction["from"]}
                dict_item["inputs"].append(dict_item_input)
                dict_item_output = {"amount": int(transaction["value"], 16) / 1E+18,
                                    "address": transaction["to"]}
                dict_item["outputs"].append(dict_item_output)
                standardized_dict.append(dict_item)

        # for transaction in json:
        #     if transaction["amount"] != 0:
        #         dict_item = {}
        #         dict_item["amount"] = transaction["amount"]/1E+18
        #         dict_item["time"] = datetime.datetime.strptime(transaction["time"].replace("T"," ")[:-5], "%Y-%m-%d %H:%M:%S")
        #         dict_item["blocktime"] = dict_item["time"]
        #         dict_item["fee"] = transaction["gasUsed"]*(transaction["price"]/ 1E+18)
        #         dict_item["hash"] = transaction["hash"]
        #         dict_item["address"] = transaction["recipient"]
        #         dict_item["block_nr"] = transaction["block_id"]
        #         standardized_dict.append(dict_item)
    elif currency == "LTC":
        for transaction in json["txs"]:
            dict_item = {"symbol": currency,
                         "time": datetime.datetime.utcfromtimestamp(json["time"]),
                         "blocktime": datetime.datetime.utcfromtimestamp(json["time"]), # same as tx time
                         "fee": transaction["fee"],
                         "hash": transaction["txid"],
                         "block_nr": json["block_no"]}
            for input in transaction["inputs"]:
                if float(input["value"]) != 0:
                    dict_item_input = {"amount": float(input["value"]),
                                       "address": input["address"]}
                    dict_item["inputs"].append(dict_item_input)
            for output in transaction["out"]:
                if float(output["value"]) != 0:
                    dict_item_output = {"amount": float(output["value"]),
                                        "address": output["address"]}
                    dict_item["outputs"].append(dict_item_output)
            standardized_dict.append(dict_item)

    else:
        print ("Couldn't standardize block for " + currency)
        return
    return standardized_dict


def get_fee_BTC(tx_hash):
    Tor.change_ip()
    for attempt in range(5):
        try:
            #fee_from = requests.get("https://chain.so/api/v2/tx/BTC/" + str(tx_hash)).json()["data"]["fee"]
            fee_from = requests.get("https://api.blockcypher.com/v1/btc/main/txs/" + str(tx_hash)).json()["fees"] / 100000000
        except:
            print ("Wait a minute. Loading BTC Fee")
            time.sleep(60)
            Tor.change_ip()
        else:
            return fee_from
    else:
        traceback.print_exc()
        sys.exit("Counldn't get fee for BTC: " + str(tx_hash))