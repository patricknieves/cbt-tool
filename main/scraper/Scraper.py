import time
from main.scraper.Shapeshift import Shapeshift
from Data_retriever import Data_retriever
from main import Database_manager

def main():
    setup_db()
    Database_manager.delete_all_scraper_data()
    get_shapeshift_exchanges()
    find_exchange_data()

def setup_db():
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()

def get_shapeshift_exchanges():
    shapeshift_manager = Shapeshift()
    start_time = time.time()
    elapsed_time = 0

    # Run a whole day
    while elapsed_time < 3*60*60:
        start_time_loop = time.time()
        shapeshift_manager.save_new_exchanges()
        duration_to_wait = shapeshift_manager.duration.total_seconds()/2
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time < duration_to_wait:
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

if __name__ == "__main__": main()