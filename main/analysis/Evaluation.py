import os
import datetime
from main import Shapeshift_api
import pandas as pd
import numpy as np


def main():

    # run_whole_analysis()

    # Or
    run_only_api_comparison()


def run_whole_analysis():
    prepare()

    # load data from excel files into dataframes
    df_scraped_data = load_scraped_data()
    df_found_data = load_tool_data()

    # Filter only entries in time range
    df_found_data = df_found_data[
        df_found_data["time_block_from"] > (df_scraped_data["time_exchange"].iloc[0] - datetime.timedelta(minutes=15))]

    # Check which exchanges were found by tool by comparing with scraped data
    result_df = compare_exchanges(df_scraped_data, df_found_data)

    # Check with help of the Shapeshift API which exchanges were additionally found and classify them
    find_with_shapeshift_api(result_df)


def run_only_api_comparison():
    prepare()
    # Load excel data into dataframe
    result_df = pd.read_csv('out_tool3.csv')

    # Check with help of the Shapeshift API which exchanges were additionally found and classify them
    find_with_shapeshift_api(result_df)


def prepare():
    # Retrieve current working directory (`cwd`)
    cwd = os.getcwd()

    # Change directory
    os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\saved addresses")

    # List all files and directories in current directory
    print(os.listdir('.'))


def load_scraped_data():
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


def load_tool_data():
    # Load data found by tool
    file = 'local_exchanges_01.02_very_high_range.csv'
    df_found_data = pd.read_csv(file)
    df_found_data['time_block_from'] = pd.to_datetime(df_found_data['time_block_from'])
    df_found_data["shapeshift"] = False
    # reverse dataframe
    df_found_data = df_found_data.iloc[::-1]
    return df_found_data


def compare_exchanges(df_scraped_data, df_found_data):
    # for i in df_scraped_data.index:
    #    for i in df_found_data.index:
    for scraper_index, scraper_row in df_scraped_data.iterrows():
        print("Searching for Exchange")
        for tool_index, tool_row in df_found_data.iterrows():
            # TODO add lower time bound
            if pd.to_datetime(tool_row["time_block_from"]) - datetime.timedelta(minutes=10) < pd.to_datetime(
                    scraper_row["time_exchange"]):
                # String comparison as float comparison is not precise
                # str(scraper_row["amount_from"]) == str(tool_row["amount_from"]) and str(scraper_row["amount_to"]) == str(tool_row["amount_to"])
                if scraper_row["address_from"] == tool_row["address_from"] and \
                                scraper_row["address_to"] == tool_row["address_to"] and \
                                scraper_row["hash_from"] == tool_row["hash_from"] and \
                                scraper_row["hash_to"] == tool_row["hash_to"]:
                    # TODO add right set_value command
                    df_scraped_data.at[scraper_index, "found"] = True
                    df_found_data.at[tool_index, "shapeshift"] = True
                    print ("found")
                    # df_scraped_data["found"][scraper_index] = True
                    # df_found_data["shapeshift"][tool_index] = True
            else:
                break

    print(len(df_scraped_data[df_scraped_data["found"] == True]))
    # print(df_scraped_data[df_scraped_data["found"] == True].head())
    print(len(df_scraped_data[df_scraped_data["found"] == False]))
    # print(df_scraped_data[df_scraped_data["found"] == False].head())

    # write result to new csv files
    df_scraped_data.to_csv('out_scraped3.csv')
    df_found_data.to_csv('out_tool3.csv')

    return df_found_data


def find_with_shapeshift_api(df_found_data):
    df_found_data["real_currency_to"] = "Not found"
    df_found_data["found_by_api"] = False
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
            if found == False:
                # If already found in first process set found so it will be skipped
                if tool_row["shapeshift"] == True:
                    found = True
                # Else add entry to group of exchanges with same address_from
                else:
                    found_exchanges_for_one_address.append({"index": tool_index, "row": tool_row})
        # Entry is in another group as previous / has another address_from
        else:
            # Exchange wasn't found before -> check with Shapeshift API if BTC/ETH exchange and if yes if corresponding Tx found
            if found == False:
                # Check with Shapeshift API if real exchange
                exchange_details = Shapeshift_api.get_exchange(found_exchanges_for_one_address[0]["row"]["address_from"])
                if exchange_details and "outgoingType" in exchange_details:

                    # Save outgoing currency
                    for exchange in found_exchanges_for_one_address:
                        df_found_data.at[exchange["index"], "real_currency_to"] = exchange_details["outgoingType"]

                    # If BTC/ETH Exchange -> check if was found by tool
                    if exchange_details["outgoingType"] == "BTC" or exchange_details["outgoingType"] == "ETH":
                        for exchange in found_exchanges_for_one_address:
                            if exchange["row"]["address_to"] == exchange_details["withdraw"] and \
                                            exchange["row"]["hash_to"] == exchange_details["transaction"]:
                                print("found!")
                                df_found_data.at[exchange["index"], "found_by_api"] = True
                                break

            # Reset values
            found = False
            found_exchanges_for_one_address = []

            # Add current row, set new last_address
            found_exchanges_for_one_address.append({"index": tool_index, "row": tool_row})
            last_address = tool_row["address_from"]
            if tool_row["shapeshift"] == True:
                found = True

    df_found_data.to_csv('final_analysis.csv')


if __name__ == "__main__": main()
