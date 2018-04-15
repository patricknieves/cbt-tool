import Tor
import time
import traceback
import requests
import operator
import os
import pandas as pd

shapeshift_main_address = "1NSc6zAdG2NGbjPLQwAjAuqjHSoq5KECT7"

def mainX():
    counter = 0
    main_addresses = set()
    main_addresses_counter_tx = []
    main_addresses_counter_inputs = {}
    current_block_nr = None
    check_until_block_nr = 476288

    start_time = time.time()

    while not current_block_nr or current_block_nr > check_until_block_nr:
        response = get_transactions(counter)
        counter = counter + 50
        for tx in response:
            if "block_height" in tx:
                current_block_nr = tx["block_height"]
                for input in tx["inputs"]:
                    if input["prev_out"]["addr"] == shapeshift_main_address:
                        for output in tx["out"]:
                            if len(str(output["value"])) > 8 and str(output["value"])[-8:] == "00000000":
                                if not output["addr"] in main_addresses:
                                    result = get_transactions_by_address(output["addr"])
                                    main_addresses.add(output["addr"])
                                    print ("address: " + str(output["addr"]) + ", count: " + str(result["n_tx"]))
                                    main_addresses_counter_tx.append({"address": output["addr"], "count": result["n_tx"]})
                                    main_addresses_counter_inputs[output["addr"]] = 1
                                else:
                                    number = main_addresses_counter_inputs[output["addr"]] + 1
                                    main_addresses_counter_inputs[output["addr"]] = number
                        break

    print("Duration:" + str(time.time() - start_time))
    print ("Finish")

def main():
    prepare()
    counter = 0
    output_addresses = set()
    output_addresses_counter = {}
    current_block_nr = None
    check_until_block_nr = 476288
    #check_until_block_nr = 509584

    start_time = time.time()

    while not current_block_nr or current_block_nr > check_until_block_nr:
        response = get_transactions(counter)
        counter = counter + 50
        for tx in response:
            if "block_height" in tx:
                current_block_nr = tx["block_height"]
                for input in tx["inputs"]:
                    if input["prev_out"]["addr"] == shapeshift_main_address:
                        for output in tx["out"]:
                            if not output["addr"] in output_addresses:
                                output_addresses.add(output["addr"])
                                output_addresses_counter[output["addr"]] = 1
                            else:
                                number = output_addresses_counter[output["addr"]] + 1
                                output_addresses_counter[output["addr"]] = number
                        break


    sorted_x = sorted(output_addresses_counter.items(), key=operator.itemgetter(1), reverse=True)
    df_scraped_data = pd.DataFrame.from_dict(sorted_x)
    df_scraped_data.to_csv('connected_addresses2.csv')
    print("Duration:" + str(time.time() - start_time))
    print ("Finish")

def prepare():
    # Retrieve current working directory (`cwd`)
    cwd = os.getcwd()

    # Change directory
    #os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\saved addresses")
    os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\New scraper")

    # List all files and directories in current directory
    print(os.listdir('.'))


def get_transactions(offset):
    Tor.change_ip()
    for attempt in range(5):
        try:
            transactions = requests.get("https://blockchain.info/de/rawaddr/" + shapeshift_main_address + "?offset=" + str(offset)).json()["txs"]
        except:
            print ("Wait 5 sec")
            time.sleep(5)
            Tor.change_ip()
        else:
            return transactions
    else:
        traceback.print_exc()
        print("Couldn't get transactions from Etherscan")

def get_transactions_by_address(address):
    Tor.change_ip()
    for attempt in range(5):
        try:
            transactions = requests.get("https://blockchain.info/de/rawaddr/" + address).json()
        except:
            print ("Wait 5 sec")
            time.sleep(5)
            Tor.change_ip()
        else:
            return transactions
    else:
        traceback.print_exc()
        print("Couldn't get transactions from Etherscan")

if __name__ == "__main__": main()