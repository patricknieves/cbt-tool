import os
import datetime
from main import Shapeshift_api
import pandas as pd
import time


def main():
    run_whole_analysis()
    # Or
    #run_only_api_comparison()


def run_whole_analysis():
    prepare()
    # load data from excel files into dataframes
    df_scraped_data = load_scraped_data()
    df_found_data = load_tool_data()

    # Filter only entries in time range
    #df_found_data = df_found_data[
    #    df_found_data["time_block_from"] > (df_scraped_data["time_exchange"].iloc[0] - datetime.timedelta(minutes=15))]

    # Check which exchanges were found by tool by comparing with scraped data
    start_compare = time.time()
    result_df = compare(df_scraped_data, df_found_data)
    print("Duration: " + str(time.time() - start_compare))

    # Check with help of the Shapeshift API which exchanges were additionally found and classify them
    start_compare_api = time.time()
    find_with_shapeshift_api(result_df)
    print("Duration: " + str(time.time() - start_compare_api))


def run_only_api_comparison():
    prepare()
    # Load excel data into dataframe
    result_df = pd.read_csv('analyzed_tool_1520850238.08.csv')

    start_compare_api = time.time()
    # Check with help of the Shapeshift API which exchanges were additionally found and classify them
    find_with_shapeshift_api(result_df)
    print("Duration: " + str(time.time() - start_compare_api))


def prepare():
    # Retrieve current working directory (`cwd`)
    cwd = os.getcwd()

    # Change directory
    #os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\saved addresses")
    os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\New scraper")

    # List all files and directories in current directory
    print(os.listdir('.'))


def load_scraped_data_old():
    # Load scraped data
    file = 'data_scraper-14.12.csv'
    # Scraped data in this case is separated by semicolons and date has to be adapted as it was transform falsely
    df_scraped_data = pd.read_csv(file, sep=';')
    df_scraped_data['time_exchange'] = pd.to_datetime(df_scraped_data['time_exchange']) - datetime.timedelta(
        days=365 * 4 + 2)
    # Filter only BTC and ETH
    df_scraped_data = df_scraped_data[
        df_scraped_data["currency_from"].isin(["BTC", "ETH"]) & df_scraped_data["currency_to"].isin(["BTC", "ETH"])]
    df_scraped_data["found"] = False
    return df_scraped_data


def load_scraped_data():
    # Load data found by tool
    file = 'server_scraped_02.03.csv'
    df_scraped_data = pd.read_csv(file, delimiter=',')

    #df_scraped_data = df_scraped_data[
    #    df_scraped_data["id"] >= 242889]
    df_scraped_data = df_scraped_data[
        248933 >= df_scraped_data["id"]]

    df_scraped_data['time_exchange'] = pd.to_datetime(df_scraped_data['time_exchange'])

    # Filter only BTC and ETH
    df_scraped_data = df_scraped_data[
        df_scraped_data["currency_from"].isin(["BTC", "ETH"]) & df_scraped_data["currency_to"].isin(["BTC", "ETH"])]
    df_scraped_data["found"] = False
    return df_scraped_data


def load_tool_data():
    # Load data found by tool
    #file = 'local_exchanges_07.02.csv'
    file = 'tool_new_15.csv'
    df_found_data = pd.read_csv(file)
    df_found_data['time_block_from'] = pd.to_datetime(df_found_data['time_block_from'])
    df_found_data["shapeshift"] = False
    # reverse dataframe
    df_found_data = df_found_data.iloc[::-1]
    return df_found_data


def compare(df_scraped_data, df_found_data):
    # scraped
    df1 = pd.merge(df_scraped_data, df_found_data, on=['address_from', 'address_to', 'hash_from', 'hash_to'], how='inner')
    # tool
    df2 = pd.merge(df_found_data, df_scraped_data, on=['address_from', 'address_to', 'hash_from', 'hash_to'], how='inner')

    # Get matching ids
    scraper_ids = set(df1["id_x"])
    tool_ids = set(df2["id_x"])

    # Compare if in matching ids
    found_in_tool = df_found_data["id"].isin(tool_ids)
    df_found_data["shapeshift"] = found_in_tool

    # Add boolean list to data frame
    found_in_scraper = df_scraped_data["id"].isin(scraper_ids)
    df_scraped_data["found"] = found_in_scraper

    print(len(df_scraped_data[df_scraped_data["found"] == True]))
    print(len(df_scraped_data[df_scraped_data["found"] == False]))
    print(len(df_found_data[df_found_data["shapeshift"] == True]))
    print(len(df_found_data[df_found_data["shapeshift"] == False]))

    # write result to new csv files
    time_now = time.time()
    df_scraped_data.to_csv('analyzed_scraper_' + str(time_now) + '.csv')
    df_found_data.to_csv('analyzed_tool_' + str(time_now) + '.csv')

    return df_found_data


def find_with_shapeshift_api(df_found_data):
    df_found_data["real_currency_to"] = "Not found"
    df_found_data["found_by_api"] = False
    df_found_data["status"] = None
    df_found_data["found_for_deposit"] = False

    last_address = None
    found_exchanges_for_one_address = []
    found = False
    i = 0

    for tool_index, tool_row in df_found_data.iterrows():
        # testing
        i = i + 1
        print("Checking tx nr. " + str(i))

        # First Entry
        if not last_address:
            last_address = tool_row["address_from"]
            found_exchanges_for_one_address.append({"index": tool_index, "row": tool_row})
            if tool_row["shapeshift"] == True:
                found = True
        # Entry is in the same group as previous / has the same address_from
        elif last_address == tool_row["address_from"]:
            found_exchanges_for_one_address.append({"index": tool_index, "row": tool_row})
            if found == False:
                # If already found in first process set found so it will be skipped
                if tool_row["shapeshift"] == True:
                    found = True
        # Entry is in another group as previous / has another address_from
        else:
            # Exchange wasn't found before -> check with Shapeshift API if BTC/ETH exchange and if yes if corresponding Tx found
            if found == False:
                # Check with Shapeshift API if real exchange
                exchange_details = Shapeshift_api.get_exchange(found_exchanges_for_one_address[0]["row"]["address_from"])

                # Add status
                for exchange in found_exchanges_for_one_address:
                    df_found_data.at[exchange["index"], "status"] = exchange_details["status"]

                if exchange_details and "outgoingType" in exchange_details:

                    # Save outgoing currency and status
                    for exchange in found_exchanges_for_one_address:
                        df_found_data.at[exchange["index"], "real_currency_to"] = exchange_details["outgoingType"]

                    # If BTC/ETH Exchange -> check if was found by tool
                    if exchange_details["outgoingType"] == "BTC" or exchange_details["outgoingType"] == "ETH":
                        for exchange in found_exchanges_for_one_address:
                            if exchange["row"]["address_to"] == exchange_details["withdraw"] and \
                                            exchange["row"]["hash_to"] == exchange_details["transaction"]:
                                print("found!")
                                df_found_data.at[exchange["index"], "found_by_api"] = True
                                for exchange in found_exchanges_for_one_address:
                                    df_found_data.at[exchange["index"], "found_for_deposit"] = True
                                break

            else:
                # Save/copy outgoing currency
                for exchange in found_exchanges_for_one_address:
                    df_found_data.at[exchange["index"], "real_currency_to"] = exchange["row"]["currency_to"]
                    df_found_data.at[exchange["index"], "found_for_deposit"] = True

            # Reset values
            found = False
            found_exchanges_for_one_address = []

            # Add current row, set new last_address
            found_exchanges_for_one_address.append({"index": tool_index, "row": tool_row})
            last_address = tool_row["address_from"]
            if tool_row["shapeshift"] == True:
                found = True

    time_now = time.time()
    df_found_data.to_csv('final_analysis_' + str(time_now) + '.csv')


if __name__ == "__main__": main()
