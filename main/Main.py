import Database_manager
import Bitcoin_To_Ether

def main():
    # Create MySQL Database and connect
    Database_manager.create_database()
    Database_manager.initialize_db()
    # Create MySQL Tables
    Database_manager.create_table_exchanges()

    # Delete all data from DB
    Database_manager.delete_all_data()

    # Find Exchanges
    Bitcoin_To_Ether.find_exchanges()


if __name__ == "__main__": main()