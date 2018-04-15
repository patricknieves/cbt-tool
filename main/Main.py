from Exchange_finder import Exchange_finder
import Database_manager
import time


def main():
    start = time.time()
    print ("starting time: " + str(start))
    # Create MySQL Database and connect
    Database_manager.initialize_db()
    # Create MySQL Tables
    Database_manager.create_table_exchanges()
    Database_manager.create_table_shapeshift_addresses_btc()

    # Delete all data from DB
    Database_manager.delete_all_data()

    # Find Exchanges
    print ("Searching for Exchanges...")
    #currencies_list = ["BTC", "ETH", "LTC"]
    currencies_list = ["BTC", "ETH"]
    # Set static block numbers instead of current block numbers
    # current_block_number_dict = {"BTC": 504330, "ETH": 4912461}
    # December data
    #current_block_number_dict = {"BTC": 499026, "ETH": 4724187}
    # February data
    current_block_number_dict = {"BTC": 511557, "ETH": 5180422}
    exchange_finder = Exchange_finder(currencies_list, current_block_number_dict=current_block_number_dict)
    exchange_finder.find_exchanges()
    print("Ending time: " + str(time.time()))
    print("Duration: " + str(time.time() - start))


if __name__ == "__main__": main()