from Exchange_finder import Exchange_finder
import Database_manager
import Currency_apis
import time
from Address_tracker_btc import Address_tracker_btc

def main():
    # Create MySQL Database and connect
    Database_manager.initialize_db()
    # Create MySQL Tables
    Database_manager.create_table_exchanges()
    Database_manager.create_table_shapeshift_addresses_btc()

    # Delete all data from DB
    Database_manager.delete_all_data()

    # Find Exchanges
    print ("Searching for Exchanges...")
    #currencies_array = ["BTC", "ETH", "LTC"]
    currencies_array = ["BTC", "ETH"]
    # Set static block numbers instead of current block numbers
    # current_block_number_dict = {"BTC": 504330, "ETH": 4912461}
    current_block_number_dict = {"BTC": 499026, "ETH": 4724187}
    exchange_finder = Exchange_finder(currencies_array, current_block_number_dict=current_block_number_dict)
    exchange_finder.find_exchanges()


def main_test():
    Database_manager.initialize_db()
    Database_manager.create_table_shapeshift_addresses_btc()
    set_shapeshift_main_addresses()
    start = time.time()
    print(start)
    tracker = Address_tracker_btc()
    for number in range(500):
        print("Check block:" + str(504601 - number))
        new_transactions = Currency_apis.get_block_by_number("BTC", 504601 - number)
        new_transactions.sort(key=lambda x: x["time"], reverse=True)
        for transaction in new_transactions:
            tracker.check_and_save_if_shapeshift_related(transaction)
    sid = tracker.shapeshift_single_addresses
    mid = tracker.shapeshift_middle_addresses
    print (time.time() - start)
    print("finish")

def set_shapeshift_main_addresses():
    shapeshift_main_addresses = ["1NoHmhqw9oTh7nNKsa5Dprjt3dva3kF1ZG",
                                 "1LASN6ra8dwR2EjAfCPcghXDxtME7a89Hk",
                                 "1BvTQTP5PJVCEz7dCU2YxgMskMxxikSruM",
                                 "1jhbBbDRdezEZ5tSsHZwuUg85Hhf4rWuz",
                                 "3K9Xd9kPskEcJk9YyZk1cbHr2jthrcN79B"]
    for address in shapeshift_main_addresses:
        Database_manager.insert_shapeshift_address_btc(address)

if __name__ == "__main__": main()