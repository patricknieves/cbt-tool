from Exchange_finder import Exchange_finder
import Database_manager

def main():
    # Create MySQL Database and connect
    Database_manager.create_database()
    Database_manager.initialize_db()
    # Create MySQL Tables
    Database_manager.create_table_exchanges()

    # Delete all data from DB
    Database_manager.delete_all_data()

    # Find Exchanges
    #print ("Searching for BTC-ETH exchanges...")
    #Exchange_finder("BTC", "ETH").find_exchanges(20*60)
    print ("Searching for ETH-BTC exchanges...")
    Exchange_finder("ETH", "BTC").find_exchanges()

    #Exchange_finder("BTC", "LTC").find_exchanges()
    #Exchange_finder("LTC", "BTC").find_exchanges()
    #Exchange_finder("ETH", "LTC").find_exchanges()
    #Exchange_finder("LTC", "ETH").find_exchanges()

if __name__ == "__main__": main()