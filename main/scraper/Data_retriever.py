from __future__ import division
from main import Currency_apis, Database_manager, Shapeshift_api, Settings
import requests
import traceback
import datetime
import time
from main import Database_manager
from main import Tor


class Data_retriever(object):
    """ Class responisble for searching additional data on a certain blockchain"""

    def __init__(self, currency, last_block_number=None, exchanges=None):
        self.currency = currency
        self.exchanges = [] if exchanges is None else exchanges
        self.current_block_number = None if last_block_number is None else last_block_number
        self.last_block_checked = None

    def prepare(self):
        """ Retrieve all exchanges without additional data and set initial block number"""
        self.exchanges = Database_manager.get_shapeshift_exchanges_by_currency(self.currency)
        self.current_block_number = Currency_apis.get_last_block_number(self.currency) - Settings.get_scraper_offset(self.currency)

    def find_exchanges(self):
        """ Main method for searching additional blockchain data"""
        start_block = self.current_block_number
        if self.last_block_checked == None:
            self.last_block_checked = start_block - Settings.get_scraper_offset_for_first_iteration(self.currency)
        print("Starting with Block" + str(self.current_block_number) + "for" + self.currency)
        while self.exchanges and (self.current_block_number > self.last_block_checked):
            transactions = Currency_apis.get_block_by_number(self.currency, self.current_block_number)
            for transaction in transactions:
             self.compare(transaction)
            self.current_block_number = self.current_block_number - 1
        print("Ending with Block " + str(self.current_block_number) + " for " + self.currency)
        self.last_block_checked = start_block - Settings.get_scraper_offset_last_block(self.currency)

    def compare(self, transaction):
        """ Check if any exchange belongs to a transaction retrieved from the blockchain """
        for exchange in list(self.exchanges):
            block_time_diff = (exchange["time_exchange"] - transaction["blocktime"]).total_seconds()
            tx_time_diff = (exchange["time_exchange"] - transaction["time"]).total_seconds()
            if tx_time_diff < -10*60:
                break
            elif tx_time_diff < 6*60:
                # Note: float rounds numbers here. str used because float comparation in python not always working.
                # This is needed if exchanges are retrieved from DB and not directly from the Shapeshift API
                for output in transaction["outputs"]:
                    if str(float(exchange["amount_from"]))[:9] == str(float(output["amount"]))[:9]:
                        if output["address"]:
                            exchange_details = Shapeshift_api.get_exchange(output["address"])
                            if not exchange_details:
                                print("No output address for tx: " + transaction["hash"])
                            else:
                                if exchange_details["status"] == "complete" and \
                                                exchange_details["outgoingType"] == exchange["currency_to"]and \
                                                exchange_details["incomingType"] == exchange["currency_from"]and \
                                                str(float(exchange_details["incomingCoin"]))[:9] == str(float(exchange["amount_from"]))[:9]:
                                    Database_manager.update_shapeshift_exchange(exchange_details["outgoingCoin"],
                                                                                transaction["fee"],
                                                                                exchange_details["address"],
                                                                                exchange_details["withdraw"],
                                                                                transaction["hash"],
                                                                                exchange_details["transaction"],
                                                                                transaction["time"],
                                                                                transaction["blocktime"],
                                                                                self.current_block_number,
                                                                                exchange["id"]
                                                                                )

                                    self.search_withdrawal_data(exchange_details, exchange)
                                    self.exchanges.remove(exchange)
                                    # break both loops
                                    return
            elif block_time_diff >= 10*60:
                self.exchanges.remove(exchange)

    def search_withdrawal_data(self, exchange_details, exchange):
        """ Search for additional data for the withdrawal transaction (Block number, tx time, block time and fee)"""
        currency = exchange_details["outgoingType"]
        tx_hash =  exchange_details["transaction"]
        exchange_id = exchange["id"]

        Tor.change_ip()
        for attempt in range(5):
            try:
                if currency == "ETH":
                    transaction = requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_getTransactionByHash?params=%5B%22" + str(tx_hash) + "%22%5D&token=Wh9YuEIhi7tqseXn8550").json()["result"]
                    block = requests.get("https://api.infura.io/v1/jsonrpc/mainnet/eth_getBlockByNumber?params=%5B%22" + str(transaction["blockNumber"]) + "%22%2C%20true%5D&token=Wh9YuEIhi7tqseXn8550").json()["result"]
                    time_to = datetime.datetime.utcfromtimestamp(int(block["timestamp"], 16)).strftime('%Y-%m-%d %H:%M:%S')
                    time_block_to = time_to
                    fee_to = int(transaction["gas"], 16)*(int(transaction["gasPrice"], 16) / 1E+18)
                    block_nr_to = int(transaction["blockNumber"], 16)
                    Database_manager.update_shapeshift_exchange_corresponding_tx(time_to, time_block_to, fee_to, block_nr_to, exchange_id)
                elif currency == "BTC":
                    transaction = requests.get("https://blockchain.info/de/rawtx/" + str(tx_hash)).json()

                    if not("block_height" in transaction):
                        print("Block not confirmed yet. Couldn't get the corresponding Transaction for " + str(tx_hash))
                        return

                    block_nr_to = int(transaction["block_height"])
                    time_to = datetime.datetime.utcfromtimestamp(transaction["time"]).strftime('%Y-%m-%d %H:%M:%S')
                    block = requests.get("https://blockchain.info/de/block-height/" + (str(block_nr_to)) + "?format=json").json()["blocks"][0]
                    time_block_to = datetime.datetime.utcfromtimestamp(block["time"])

                    # Calculate fee
                    input_value = 0
                    output_value = 0
                    for tx_input in transaction["inputs"]:
                        if "prev_out" in tx_input and tx_input["prev_out"]["value"] != 0 and "addr" in tx_input["prev_out"]:
                            input_value = input_value + tx_input["prev_out"]["value"] / 100000000
                    for tx_output in transaction["out"]:
                        if tx_output["value"] != 0 and "addr" in tx_output:
                            output_value = output_value + tx_output["value"] / 100000000
                    fee_to = input_value - output_value
                    # Don't save if coinbase transaction
                    if input_value != 0:
                        Database_manager.update_shapeshift_exchange_corresponding_tx(time_to, time_block_to, fee_to, block_nr_to, exchange_id)
            except:
                print ("Wait half a minute")
                time.sleep(30)
                Tor.change_ip()
            else:
                break
        else:
            traceback.print_exc()
            print("Couldn't get the corresponding Transaction for " + str(currency))


def main():
    """ Method to start the Data retriever for Bitcoin and Ethereum"""
    setup_db()
    btc_finder = Data_retriever("BTC")
    eth_finder = Data_retriever("ETH")
    while True:
        start_time = time.time()

        print ("Searching for BTC exchanges...")
        btc_finder.prepare()
        btc_finder.find_exchanges()
        print ("Searching for ETH exchanges...")
        eth_finder.prepare()
        eth_finder.find_exchanges()

        elapsed_time = time.time() - start_time
        if elapsed_time < 30*60:
            print("Waiting 30 min for next loop")
            time.sleep(30*60)

def setup_db():
    """ Database Setup """
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()


if __name__ == "__main__": main()