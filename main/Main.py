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
    print ("Searching for Exchanges...")
    #currencies_array = ["BTC", "ETH", "LTC"]
    currencies_array = ["BTC", "ETH"]
    # Set static block numbers instead of current block numbers
    current_block_number_dict = {"BTC": 504330, "ETH": 4912461}
    exchange_finder = Exchange_finder(currencies_array, current_block_number_dict=current_block_number_dict)
    exchange_finder.find_exchanges()

if __name__ == "__main__": main()