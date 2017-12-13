import time
from threading import Thread
from main.scraper.Shapeshift import Shapeshift
from Data_retriever import Data_retriever
from main import Database_manager


def main():
    setup_db()
    Database_manager.delete_all_scraper_data()
    get_shapeshift_exchanges(5*60)
    find_exchange_data()


# Use this method when Exchanges Table already filled but additional data still wasn't found
def main_find_from_exact_block():
    Database_manager.initialize_db()
    find_exchange_data_from_exact_block()


def setup_db():
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()


def get_shapeshift_exchanges(runtime_in_sec):
    shapeshift_manager = Shapeshift()
    start_time = time.time()
    elapsed_time = 0
    # Run a whole day
    while elapsed_time < runtime_in_sec:
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration.total_seconds()/2
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)
        elapsed_time = time.time() - start_time


def get_shapeshift_exchanges_instant(runtime_in_sec):
    shapeshift_manager = Shapeshift()
    start_time = time.time()
    elapsed_time = 0

    # Run a whole day
    while elapsed_time < runtime_in_sec:
        start_time_loop = time.time()
        new_exchanges = shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration.total_seconds()/2
        t = Thread(target=find_exchange_data, args=())
        #t = Thread(target=find_exchange_data, args=(new_exchanges,))
        t.start()
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)
        elapsed_time = time.time() - start_time


def find_exchange_data():
    btc_finder = Data_retriever("BTC")
    eth_finder = Data_retriever("ETH")
    ltc_finder = Data_retriever("LTC")
    print ("Searching for BTC exchanges...")
    btc_finder.find_exchanges()
    print ("Searching for ETH exchanges...")
    eth_finder.find_exchanges()
    print ("Searching for LTC exchanges...")
    ltc_finder.find_exchanges()
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
    btc_finder = Data_retriever("BTC", 498732)
    eth_finder = Data_retriever("ETH", 4713307)
    ltc_finder = Data_retriever("LTC", 1330146)
    print ("Searching for BTC exchanges...")
    btc_finder.find_exchanges()
    print ("Searching for ETH exchanges...")
    eth_finder.find_exchanges()
    print ("Searching for LTC exchanges...")
    ltc_finder.find_exchanges()

if __name__ == "__main__": main()