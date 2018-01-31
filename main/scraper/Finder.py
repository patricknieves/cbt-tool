import time
from main import Database_manager
from Data_retriever import Data_retriever

def find():
    #setup_db()
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
        if elapsed_time < 3*60:
            print("Waiting 30 min for next loop")
            time.sleep(3*60)

# Use this method when Exchanges Table already filled but additional data still wasn't found
def main_find_from_exact_block():
    Database_manager.initialize_db()
    find_exchange_data_from_exact_block()

def setup_db():
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()


def find_exchange_data():
    btc_finder = Data_retriever("BTC")
    eth_finder = Data_retriever("ETH")
    #ltc_finder = Data_retriever("LTC")
    print ("Searching for BTC exchanges...")
    btc_finder.find_exchanges()
    print ("Searching for ETH exchanges...")
    eth_finder.find_exchanges()
    #print ("Searching for LTC exchanges...")
    #ltc_finder.find_exchanges()
    print ("Finished Search!")


def find_exchange_data_instant(exchanges):
    btc_finder = Data_retriever("BTC", exchanges=[exchange for exchange in exchanges if "BTC" == exchange["currency_from"]])
    eth_finder = Data_retriever("ETH", exchanges=[exchange for exchange in exchanges if "ETH" == exchange["currency_from"]])
    ltc_finder = Data_retriever("LTC", exchanges=[exchange for exchange in exchanges if "LTC" == exchange["currency_from"]])
    print ("Searching for BTC exchanges...")
    btc_finder.find_exchanges()
    print ("Searching for ETH exchanges...")
    eth_finder.find_exchanges()
    print ("Searching for LTC exchanges...")
    ltc_finder.find_exchanges()
    print ("Finished Search!")


def find_exchange_data_from_exact_block():
    btc_finder = Data_retriever("BTC", 498992)
    eth_finder = Data_retriever("ETH", 4723750)
    ltc_finder = Data_retriever("LTC", 1331127)
    print ("Searching for BTC exchanges...")
    btc_finder.find_exchanges()
    print ("Searching for ETH exchanges...")
    eth_finder.find_exchanges()
    print ("Searching for LTC exchanges...")
    ltc_finder.find_exchanges()
