from main import Database_manager
import time
from threading import Thread
from Shapeshift import Shapeshift
from Data_retriever import Data_retriever


def main():
    """ Main method to start all components of the scraper """
    setup_db()
    #Database_manager.delete_all_scraper_data()
    get_shapeshift_exchanges()


def setup_db():
    """ Database setup """
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()


def get_shapeshift_exchanges():
    """ initializes all components and runs them """
    shapeshift_manager = Shapeshift()
    t = Thread(target=find_blockchain_data, args=())
    t.start()
    while True:
        if not t.isAlive():
            print("Starting finder again!")
            t.start()
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)


def find_blockchain_data():
    """ Starts the Data Retriever for Bitcoin and Ethereum """
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


if __name__ == "__main__": main()