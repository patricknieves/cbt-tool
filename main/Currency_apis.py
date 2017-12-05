import Tor
import time
import requests
import traceback
import sys

def get_last_block_number_BTC():
    Tor.change_ip()
    for attempt in range(10):
        try:
            last_block_number = requests.get("https://blockchain.info/de/latestblock").json()["height"]
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return last_block_number
    else:
        traceback.print_exc()
        sys.exit("Counldn't get last number of block from Blockchain.info")


def get_block_by_number_BTC(number):
    Tor.change_ip()
    for attempt in range(5):
        try:
            block = requests.get("https://blockchain.info/de/block-height/" + (str(number)) + "?format=json").json()["blocks"][0]
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return block
    else:
        traceback.print_exc()
        sys.exit("Counldn't get block from Blockchain: " + str(number))


def get_fee_BTC(tx_hash):
    # Get fee_from
    Tor.change_ip()
    for attempt in range(5):
        try:
            fee_from = requests.get("https://chain.so/api/v2/tx/BTC/" + str(tx_hash)).json()["data"]["fee"]
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return fee_from
    else:
        for attempt in range(5):
            try:
                fee_from = requests.get("https://api.blockcypher.com/v1/btc/main/txs/" + str(hash)).json()["fees"] / 100000000
            except:
                print ("Wait a minute")
                time.sleep(60)
                Tor.change_ip()
            else:
                return fee_from
        else:
            traceback.print_exc()
            sys.exit("Counldn't get fee for BTC: " + str(tx_hash))


def get_last_block_number_ETH():
    for attempt in range(10):
        try:
            last_block_number = requests.get("https://etherchain.org/api/blocks/count").json()["data"][0]["count"]
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return last_block_number
    else:
        traceback.print_exc()
        sys.exit("Counldn't get last number of block from Etherchain.org")


def get_last_block_by_number_ETH(number):
    Tor.change_ip()
    for attempt in range(5):
        try:
            transactions = requests.get("https://etherchain.org/api/block/" + (str(number)) + "/tx").json()["data"]
        except:
            print ("Wait a minute")
            time.sleep(60)
            Tor.change_ip()
        else:
            return transactions
    else:
        traceback.print_exc()
        sys.exit("Counldn't get block from Etherchain: " + str(number))