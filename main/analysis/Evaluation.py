import os
import datetime
from main import Shapeshift_api
import pandas as pd
import numpy as np

# Retrieve current working directory (`cwd`)
cwd = os.getcwd()
# Change directory
os.chdir("C:\\Users\\Patrick\\Documents\\TUM\\13. Semester\\Masterarbeit\\Crawler\\saved addresses")

# List all files and directories in current directory
print(os.listdir('.'))

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

# Load scraped data
file = 'local_exchanges_01.02_very_high_range.csv'
df_found_data = pd.read_csv(file)
df_found_data['time_block_from'] = pd.to_datetime(df_found_data['time_block_from'])
df_found_data["shapeshift"] = False
# reverse dataframe
df_found_data = df_found_data.iloc[::-1]
# Filter only entries in time range
df_found_data = df_found_data[df_found_data["time_block_from"] > (df_scraped_data["time_exchange"].iloc[0] - datetime.timedelta(minutes=15))]

# Print the sheet names
#print(df_scraped_data.head())

# for i in df_scraped_data.index:
#    for i in df_found_data.index:
for scraper_index, scraper_row in df_scraped_data.iterrows():
    print("Searching for Exchange")
    for tool_index, tool_row in df_found_data.iterrows():
        # TODO add lower time bound
        if pd.to_datetime(tool_row["time_block_from"]) - datetime.timedelta(minutes=10) < pd.to_datetime(scraper_row["time_exchange"]):
            # String comparison as float comparison is not precise
            if str(scraper_row["amount_from"]) == str(tool_row["amount_from"]) and \
                            str(scraper_row["amount_to"]) == str(tool_row["amount_to"]) and \
                            scraper_row["address_from"] == tool_row["address_from"] and \
                            scraper_row["address_to"] == tool_row["address_to"] and \
                            scraper_row["hash_from"] == tool_row["hash_from"] and \
                            scraper_row["hash_to"] == tool_row["hash_to"]:
                # TODO add right set_value command
                df_scraped_data.at[scraper_index, "found"] = True
                df_found_data.at[tool_index, "shapeshift"] = True
                print ("found")
                #df_scraped_data["found"][scraper_index] = True
                #df_found_data["shapeshift"][tool_index] = True
        else:
            break

print(len(df_scraped_data[df_scraped_data["found"] == True]))
#print(df_scraped_data[df_scraped_data["found"] == True].head())
print(len(df_scraped_data[df_scraped_data["found"] == False]))
#print(df_scraped_data[df_scraped_data["found"] == False].head())

# write result to new csv files
df_scraped_data.to_csv('out_scraped2.csv')
df_found_data.to_csv('out_tool2.csv')


def find_with_shapeshift_api():
    last_address = None
    found_exchanges_for_one_address = []
    found = False

    for tool_index, tool_row in df_found_data.iterrows():
        # First Entry
        if not last_address:
            last_address = tool_row["address_from"]
            found_exchanges_for_one_address.append({"index":tool_index, "row":tool_row})
            if tool_row["shapeshift"] == True:
                found = True
        # Entry is in the same group as previous / has the same address_from
        elif last_address == tool_row["address_from"]:
            # If already found in first process skip
            if found == True:
                continue
            elif tool_row["shapeshift"] == True:
                found = True
                continue
            # Else add entry to group of exchanges with same address_from
            else:
                found_exchanges_for_one_address.append({"index":tool_index, "row":tool_row})
                continue
        # Entry is in another group as previous / has another address_from
        else:
            # Exchnage wasn't found before -> check with Shapeshift API if BTC/ETH exchange and if yes if corresponding Tx found
            if found == False:
                Shapeshift_api.get_exchange(tool_row["address_from"])
                # TODO ETH/BTC? & right output?

            # Reset values
            found = False
            found_exchanges_for_one_address = []

            # Add current row, set new last_address
            found_exchanges_for_one_address.append({"index":tool_index, "row":tool_row})
            last_address = tool_row["address_from"]
            if tool_row["shapeshift"] == True:
                found = True
