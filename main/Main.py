from Exchange_finder import Exchange_finder
import Database_manager
import Currency_apis
import time
import os
from Address_tracker_btc import Address_tracker_btc

from pycoin.blockchain.BlockChain import BlockChain
from pycoin.block import Block
from main.bitcoin_disk import Blockfiles
import bitcoin_disk

def main():
    b = BlockChain()
    print(str(b.last_block_hash()))
    #path_BTC = os.path.join = ("E:", "Masterarbeit", "btc_node")
    bf = Blockfiles(base_dir="E:\\Masterarbeit\\btc_node")
    print(bf._path_for_file_index())
    block = Block.parse_as_header(bf)
    #bitcoin_disk.blockheader_for_offset_info((0, 0), base_dir="E:\\Masterarbeit\\btc_node")
    for block in bitcoin_disk.locked_blocks_iterator(start_info=(0, 0), base_dir="E:\\Masterarbeit\\btc_node"):
        print("Block")
        print(block.version)
        print(block.previous_block_hash)
        print(block.merkle_root)
        print(block.timestamp)
        print(block.difficulty)
        print(block.nonce)
        for tx in block.txs:
            #mytx = Tx(tx)
            #print(mytx.txs_in)
            print("Tx")
            print(tx.version)
            print(tx.lock_time)
            print(tx.unspents)
            for tx_in in tx.txs_in:
                print("Input")
                #print(str(tx_in.address))
                print(str(tx_in.previous_hash))
                print(str(tx_in.previous_index))
                print(str(tx_in.script))
                print(str(tx_in.sequence))
                print(str(tx_in.witness))
            for tx_out in tx.txs_out:
                print("Output")
                print(str(tx_out.coin_value))
                print(str(tx_out.script))


def mainX():
    print ("starting time: " + str(time.time()))
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
    print("Ending time: " + str(time.time()))

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