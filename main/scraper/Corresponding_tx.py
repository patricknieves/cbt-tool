from __future__ import division
import requests
import traceback
import datetime
import sys
import time
from main import Database_manager
from main import Tor


def search_corresponding_transaction(currency, tx_hash, exchange_id):
    Tor.change_ip()
    for attempt in range(5):
        try:
            if currency == "ETH":
                transaction = requests.get("https://etherchain.org/api/tx/" + str(tx_hash)).json()["data"][0]
                time_to = transaction["time"].replace("T"," ")[:-5]
                fee_to = transaction["gasUsed"]*(transaction["price"]/ 1E+18)
            elif currency == "BTC":
                transaction = requests.get("https://chain.so/api/v2/tx/BTC/" + str(tx_hash)).json()["data"]
                time_to = datetime.datetime.utcfromtimestamp(transaction["time"]).strftime('%Y-%m-%d %H:%M:%S')
                fee_to = transaction["fee"]
            elif currency == "LTC":
                transaction = requests.get("https://chain.so/api/v2/tx/LTC/" + str(tx_hash)).json()["data"]
                time_to = datetime.datetime.utcfromtimestamp(transaction["time"]).strftime('%Y-%m-%d %H:%M:%S')
                fee_to = transaction["fee"]
            Database_manager.cur.execute("UPDATE scraper SET  time_to = %s, fee_to = %s WHERE id = %s", (time_to, fee_to, exchange_id))
            Database_manager.db.commit()
        except:
            print ("Wait a minute")
            time.sleep(30)
            Tor.change_ip()
        else:
            break
    else:
        search_corresponding_transaction2(currency, tx_hash, exchange_id)

def search_corresponding_transaction2(currency, tx_hash, exchange_id):
    Tor.change_ip()
    for attempt in range(5):
        try:
            if currency == "ETH":
                transaction = requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_getTransactionByHash?params=%5B%22" + str(tx_hash) + "%22%5D&token=Wh9YuEIhi7tqseXn8550").json()["result"]
                block = requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_getBlockByNumber?params=%5B%22" + str(transaction["blockNumber"]) + "%22%2C%20true%5D&token=Wh9YuEIhi7tqseXn8550").json()["result"]
                time_to = datetime.datetime.utcfromtimestamp(int(block["timestamp"], 16)).strftime('%Y-%m-%d %H:%M:%S')
                fee_to = int(transaction["gas"], 16)*(int(transaction["gasPrice"], 16) / 1E+18)
            elif currency == "BTC":
                transaction = requests.get("https://api.blockcypher.com/v1/btc/main/txs/" + str(tx_hash)).json()
                time_to = transaction["received"].replace("T", " ")[:-5]
                fee_to = transaction["fees"] / 100000000
            elif currency == "LTC":
                transaction = requests.get("https://api.blockcypher.com/v1/ltc/main/txs/" + str(tx_hash)).json()
                time_to = transaction["received"].replace("T", " ")[:-5]
                fee_to = transaction["fees"] / 100000000
            Database_manager.cur.execute("UPDATE scraper SET  time_to = %s, fee_to = %s WHERE id = %s", (time_to, fee_to, exchange_id))
            Database_manager.db.commit()
        except:
            print ("Wait a minute")
            time.sleep(30)
            Tor.change_ip()
        else:
            break
    else:
        traceback.print_exc()
        sys.exit("Couldn't get the corresponding Transaction for " + str(currency))