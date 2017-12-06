import Database_manager
from Exchange_finder import Exchange_finder

def main():
    # Create MySQL Database and connect
    Database_manager.create_database()
    Database_manager.initialize_db()
    # Create MySQL Tables
    Database_manager.create_table_exchanges()

    # Delete all data from DB
    Database_manager.delete_all_data()

    # Find Exchanges
    btc2eth_finder = Exchange_finder("BTC", "ETH")
    btc2eth_finder.find_exchanges()
    eth2btc_finder = Exchange_finder("ETH", "BTC")
    eth2btc_finder.find_exchanges()
    btc2ltc_finder = Exchange_finder("BTC", "LTC")
    btc2ltc_finder.find_exchanges()
    ltc2btc_finder = Exchange_finder("LTC", "BTC")
    ltc2btc_finder.find_exchanges()
    eth2ltc_finder = Exchange_finder("ETH", "LTC")
    eth2ltc_finder.find_exchanges()
    ltc2eth_finder = Exchange_finder("LTC", "ETH")
    ltc2eth_finder.find_exchanges()

if __name__ == "__main__": main()