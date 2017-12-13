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
                last_block_number = requests.get("https://etherchain.org/api/blocks/count").json()["data"][0]["count"]
            elif currency == "LTC":
                last_block_number = requests.get("https://chain.so/api/v2/get_info/LTC").json()["data"]["blocks"]
                #last_block_number = requests.get("https://api.blockcypher.com/v1/ltc/main").json()["height"]
            else:
                print ("Couldn't get last number of block. Not such a currency: " + currency)
                return
        except:
            print ("Wait a minute")
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
                block = requests.get("https://etherchain.org/api/block/" + (str(number)) + "/tx").json()["data"]
            elif currency == "LTC":
                block = requests.get("https://chain.so/api/v2/block/LTC/" + (str(number))).json()["data"]
            else:
                print ("Couldn't get block. Not such a currency: " + currency)
                return
        except:
            print ("Wait a minute")
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
            for output in transaction["out"]:
                if output["value"] != 0 and "addr" in output:
                    dict_item = {}
                    dict_item["amount"] = output["value"]/100000000
                    dict_item["time"] = datetime.datetime.utcfromtimestamp(transaction["time"])
                    dict_item["blocktime"] = datetime.datetime.utcfromtimestamp(json["time"])
                    dict_item["fee"] = None
                    dict_item["hash"] = transaction["hash"]
                    dict_item["address"] = output["addr"]
                    standardized_dict.append(dict_item)
    elif currency == "ETH":
        for transaction in json:
            if transaction["amount"] != 0:
                dict_item = {}
                dict_item["amount"] = transaction["amount"]/1E+18
                dict_item["time"] = datetime.datetime.strptime(transaction["time"].replace("T"," ")[:-5], "%Y-%m-%d %H:%M:%S")
                dict_item["blocktime"] = dict_item["time"]
                dict_item["fee"] = transaction["gasUsed"]*(transaction["price"]/ 1E+18)
                dict_item["hash"] = transaction["hash"]
                dict_item["address"] = transaction["recipient"]
                standardized_dict.append(dict_item)
    elif currency == "LTC":
        for transaction in json["txs"]:
            for output in transaction["outputs"]:
                if float(output["value"]) != 0:
                    dict_item = {}
                    dict_item["amount"] = float(output["value"])
                    dict_item["time"] = datetime.datetime.utcfromtimestamp(json["time"])
                    dict_item["blocktime"] = dict_item["time"]
                    dict_item["fee"] = transaction["fee"]
                    dict_item["hash"] = transaction["txid"]
                    dict_item["address"] = output["address"]
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
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return fee_from
    else:
        traceback.print_exc()
        sys.exit("Counldn't get fee for BTC: " + str(tx_hash))