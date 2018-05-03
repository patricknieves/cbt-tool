import MySQLdb
import atexit
import traceback


class DB:
    """ Class responsible for handling the connection to the Dababase and all requests """
    conn = None

    def connect(self):
        """ Connects to the DB """
        self.conn = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017", db="cross_block")

    def query(self, sql, parameters=None):
        """ Performs a SQL query with the given parameters """
        try:
            cursor = self.conn.cursor()
            if parameters is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, parameters)
            cursor.close()
        except (AttributeError, MySQLdb.OperationalError, MySQLdb.ProgrammingError):
            print("RECONNECTING TO DB")
            self.connect()
            cursor = self.conn.cursor()
            if parameters is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, parameters)
            cursor.close()
        except:
            traceback.print_exc()
            print ("Error in query. Skipping")

    def query_multiple(self, sql, parameters):
        """ Performs multiple SQL queries with one command """
        try:
            cursor = self.conn.cursor()
            if parameters:
                cursor.executemany(sql, parameters)
            cursor.close()
        except (AttributeError, MySQLdb.OperationalError, MySQLdb.ProgrammingError):
            print("RECONNECTING TO DB")
            self.connect()
            cursor = self.conn.cursor()
            if parameters:
                cursor.executemany(sql, parameters)
            cursor.close()
        except:
            traceback.print_exc()
            print ("Error in query. Skipping")

    def query_get(self, sql, parameters=None):
        """ Performs a get query and returns result """
        try:
            cursor = self.conn.cursor()
            if parameters is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, parameters)
            result = cursor.fetchall()
            cursor.close()
        except (AttributeError, MySQLdb.OperationalError, MySQLdb.ProgrammingError):
            print("RECONNECTING TO DB")
            self.connect()
            cursor = self.conn.cursor()
            if parameters is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, parameters)
            result = cursor.fetchall()
            cursor.close()
        except:
            result = None
            traceback.print_exc()
            print ("Error in query. Skipping")
        return result

    def commit(self):
        """ Commits changes to the DB """
        try:
            self.conn.commit()
        except (AttributeError, MySQLdb.OperationalError, MySQLdb.ProgrammingError):
            print("RECONNECTING TO DB")
            self.connect()
            self.conn.commit()
        except:
            traceback.print_exc()
            print ("Error in query. Skipping")


def create_database():
    """ Creates the database """
    db = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017")
    cur = db.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS cross_block")
    db.close()


def initialize_db():
    """ Calls method for creating the DB and instantiates Class for handling communication to the DB """
    create_database()
    global dbClass
    dbClass = DB()
    atexit.register(closeConnection)


def create_table_exchanges():
    """ Creates table for data found by the tool """
    dbClass.query("CREATE TABLE IF NOT EXISTS exchanges ("
                "id int(11) NOT NULL AUTO_INCREMENT,"
                "currency_from varchar(45) DEFAULT NULL,"
                "currency_to varchar(45) DEFAULT NULL,"
                "amount_from DECIMAL(26, 20) DEFAULT NULL,"
                "amount_to DECIMAL(26, 20) DEFAULT NULL,"
                "fee_from DECIMAL(26, 20) DEFAULT NULL,"
                "fee_to DECIMAL(26, 20) DEFAULT NULL,"
                "fee_exchange DECIMAL(26, 20) DEFAULT NULL,"
                "address_from varchar(120) DEFAULT NULL,"
                "address_to varchar(120) DEFAULT NULL,"
                "hash_from varchar(120) DEFAULT NULL,"
                "hash_to varchar(120) DEFAULT NULL,"
                "time_from datetime DEFAULT NULL,"
                "time_block_from datetime DEFAULT NULL,"
                "time_to datetime DEFAULT NULL,"
                "time_block_to datetime DEFAULT NULL,"
                "block_nr_from int(11) DEFAULT NULL,"
                "block_nr_to int(11) DEFAULT NULL,"
                "dollarvalue_from float DEFAULT NULL,"
                "dollarvalue_to float DEFAULT NULL,"
                "exchanger varchar(120) DEFAULT NULL,"
                "PRIMARY KEY (id))")


def create_table_scraper():
    """ Creates for data retrieved by the scraper """
    dbClass.query("CREATE TABLE IF NOT EXISTS scraper_second ("
                "id int(11) NOT NULL AUTO_INCREMENT,"
                "currency_from varchar(45) DEFAULT NULL,"
                "currency_to varchar(45) DEFAULT NULL,"
                "amount_from DECIMAL(26, 20) DEFAULT NULL,"
                "amount_to DECIMAL(26, 20) DEFAULT NULL,"
                "fee_from DECIMAL(26, 20) DEFAULT NULL,"
                "fee_to DECIMAL(26, 20) DEFAULT NULL,"
                "fee_exchange float DEFAULT NULL,"
                "address_from varchar(120) DEFAULT NULL,"
                "address_to varchar(120) DEFAULT NULL,"
                "hash_from varchar(120) DEFAULT NULL,"
                "hash_to varchar(120) DEFAULT NULL,"
                "time_from datetime DEFAULT NULL,"
                "time_block_from datetime DEFAULT NULL,"
                "time_exchange datetime DEFAULT NULL,"
                "time_to datetime DEFAULT NULL,"
                "time_block_to datetime DEFAULT NULL,"
                "block_nr_from int(11) DEFAULT NULL,"
                "block_nr_to int(11) DEFAULT NULL,"
                "dollarvalue_from float DEFAULT NULL,"
                "dollarvalue_to float DEFAULT NULL,"
                "PRIMARY KEY (id))")

def create_table_shapeshift_addresses_btc():
    """ Creates a table for addresses found by the Bitcoin recognition algorithm """
    dbClass.query("CREATE TABLE IF NOT EXISTS shapeshift_addr_btc ("
                "id int(11) NOT NULL AUTO_INCREMENT,"
                "address varchar(120) DEFAULT NULL,"
                "classification varchar(120) DEFAULT NULL,"
                "PRIMARY KEY (id),"
                "UNIQUE INDEX address_UNIQUE (address ASC))")

def insert_shapeshift_address_btc(shapeshift_address, classification):
    """ Inserts Bitcoin addresses found by the Address recognition """
    try:
        dbClass.query("INSERT IGNORE INTO shapeshift_addr_btc (address, classification) VALUES (%s, %s)", (shapeshift_address, classification))
        dbClass.commit()
    except:
        print("Problem saving Shapeshift Address: "
              "Address: " + str(shapeshift_address))
        traceback.print_exc()

def create_table_shapeshift_addresses_btc_end():
    """ Creates a table for addresses found by the Bitcoin recognition algorithm - Testing """
    dbClass.query("CREATE TABLE IF NOT EXISTS shapeshift_addr_btc_end ("
                  "id int(11) NOT NULL AUTO_INCREMENT,"
                  "address varchar(120) DEFAULT NULL,"
                  "classification varchar(120) DEFAULT NULL,"
                  "PRIMARY KEY (id),"
                  "UNIQUE INDEX address_UNIQUE (address ASC))")

def insert_shapeshift_address_btc_end(shapeshift_address, classification):
    """ Inserts Bitcoin addresses found by the Address recognition - Testing """
    try:
        dbClass.query("INSERT IGNORE INTO shapeshift_addr_btc_end (address, classification) VALUES (%s, %s)", (shapeshift_address, classification))
        dbClass.commit()
    except:
        print("Problem saving Shapeshift Address: "
              "Address: " + str(shapeshift_address))
        traceback.print_exc()

def insert_exchange(currency_from,
                    currency_to,
                    amount_from,
                    amount_to,
                    fee_from,
                    fee_to,
                    fee_exchange,
                    address_from,
                    address_to,
                    hash_from,
                    hash_to,
                    time_from,
                    time_block_from,
                    time_to,
                    time_block_to,
                    block_nr_from,
                    block_nr_to,
                    dollarvalue_from,
                    dollarvalue_to,
                    exchanger
                    ):
    """ Inserts one transaction pair found by the tool """
    try:
        dbClass.query(
            "INSERT INTO exchanges ("
            "currency_from, "
            "currency_to,"
            "amount_from,"
            "amount_to,"
            "fee_from,"
            "fee_to,"
            "fee_exchange,"
            "address_from,"
            "address_to,"
            "hash_from,"
            "hash_to,"
            "time_from,"
            "time_block_from,"
            "time_to,"
            "time_block_to,"
            "block_nr_from,"
            "block_nr_to,"
            "dollarvalue_from,"
            "dollarvalue_to,"
            "exchanger"
            ") "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (currency_from,
             currency_to,
             amount_from,
             amount_to,
             fee_from,
             fee_to,
             fee_exchange,
             address_from,
             address_to,
             hash_from,
             hash_to,
             time_from,
             time_block_from,
             time_to,
             time_block_to,
             block_nr_from,
             block_nr_to,
             dollarvalue_from,
             dollarvalue_to,
             exchanger
             ))
        dbClass.commit()
    except:
        print("Problem saving Exchange: "
              "hash_from: " + str(hash_from) + " hash_to: " + str(hash_to))
        traceback.print_exc()

def insert_multiple_exchanges(parameter_list):
    """ Inserts multiple transaction pairs found by the tool """
    try:
        dbClass.query_multiple(
            "INSERT INTO exchanges ("
            "currency_from, "
            "currency_to,"
            "amount_from,"
            "amount_to,"
            "fee_from,"
            "fee_to,"
            "fee_exchange,"
            "address_from,"
            "address_to,"
            "hash_from,"
            "hash_to,"
            "time_from,"
            "time_block_from,"
            "time_to,"
            "time_block_to,"
            "block_nr_from,"
            "block_nr_to,"
            "dollarvalue_from,"
            "dollarvalue_to,"
            "exchanger"
            ") "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            parameter_list)
        dbClass.commit()
    except:
        print("Problem saving Exchanges")
        traceback.print_exc()

def insert_shapeshift_exchange(currency_from,
                               currency_to,
                               amount_from,
                               time_exchange,
                               fee_exchange,
                               dollarvalue_from,
                               dollarvalue_to
                               ):
    """ Inserts data from the Shapeshift API retrieved by the scraper """
    try:
        dbClass.query(
            "INSERT INTO scraper_second ("
            "currency_from, "
            "currency_to, "
            "amount_from, "
            "time_exchange, "
            "fee_exchange, "
            "dollarvalue_from, "
            "dollarvalue_to) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (currency_from,
             currency_to,
             amount_from,
             time_exchange,
             fee_exchange,
             dollarvalue_from,
             dollarvalue_to
             ))
        dbClass.commit()
    except:
        print("Problem saving Transaction")
        traceback.print_exc()

def get_all_shapeshift_middle_addresses_btc(classification):
    """ Returns all identified Bitcoin addresses previously saved to the DB """
    standardized_set = set([])
    try:
        results = dbClass.query_get("SELECT * FROM cross_block.shapeshift_addr_btc WHERE classification = %s", (classification,))
        for row in results:
            standardized_set.add(row[1])
    except:
        print("Problem retrieving Shapeshift Addresses from DB")
        traceback.print_exc()
    return standardized_set


def get_shapeshift_exchanges_by_currency(currency):
    """ Returns all exchanges for a given currency for which no additional data was found yet """
    standardized_dict = []
    try:
        results = dbClass.query_get("SELECT * FROM cross_block.scraper_second WHERE amount_to IS NULL AND currency_from = %s", (currency,))
        for row in results:
            dict_item = {"id": row[0],
                         "currency_from": row[1],
                         "currency_to": row[2],
                         "amount_from": row[3],
                         "time_exchange": row[14]}
            standardized_dict.append(dict_item)
    except:
        print("Problem retrieving Exchanges from DB")
        traceback.print_exc()
    return list(reversed(standardized_dict))


def update_shapeshift_exchange(amount_to,
                               fee_from,
                               address_from,
                               address_to,
                               hash_from,
                               hash_to,
                               time_from,
                               time_block_from,
                               block_nr_from,
                               id
                               ):
    """ Inserts additional data found by the scraper on the blockchain """
    try:
        dbClass.query(
            "UPDATE scraper_second SET  "
            "amount_to = %s, "
            "fee_from = %s, "
            "address_from = %s, "
            "address_to = %s, "
            "hash_from = %s, "
            "hash_to = %s, "
            "time_from = %s, "
            "time_block_from = %s, "
            "block_nr_from = %s "
            "WHERE id = %s",
            (amount_to,
             fee_from,
             address_from,
             address_to,
             hash_from,
             hash_to,
             time_from,
             time_block_from,
             block_nr_from,
             id
             ))
        dbClass.commit()
    except:
        print("Problem updating found Transaction with id: " + str(id))
        traceback.print_exc()


def update_shapeshift_exchange_corresponding_tx(time_to, time_block_to, fee_to, block_nr_to, id):
    """ Inserts additional data for the withdrawal transactions found by the scraper on the blockchain """
    try:
        dbClass.query(
            "UPDATE scraper_second SET  "
            "time_to = %s, "
            "time_block_to = %s, "
            "fee_to = %s, "
            "block_nr_to = %s "
            "WHERE id = %s",
            (time_to,
             time_block_to,
             fee_to,
             block_nr_to,
             id
             ))
        dbClass.commit()
    except:
        print("Problem updating found Transaction with id: " + str(id))
        traceback.print_exc()

def create_test_table_relations():
    """ Creates table with all steps of the Bitcoin address recognition """
    dbClass.query("CREATE TABLE IF NOT EXISTS relations ("
                  "id int(11) NOT NULL AUTO_INCREMENT,"
                  "input_address varchar(120) DEFAULT NULL,"
                  "output_address varchar(120) DEFAULT NULL,"
                  "hash_address varchar(120) DEFAULT NULL, "
                  "PRIMARY KEY (id))")

def insert_relation(input_address, output_address, hash_address):
    """ Inserts a step of the Bitcoin address recognition which shows the relation between two identified addresses """
    try:
        dbClass.query("INSERT IGNORE INTO relations (input_address, output_address, hash_address) VALUES (%s, %s, %s)", (input_address, output_address, hash_address))
        dbClass.commit()
    except:
        print("Problem saving Shapeshift Address: "
              "Address: " + str(hash_address))
        traceback.print_exc()

def get_relations(addr):
    """ Returns one step of the Bitcoin address recognition for a given address """
    results = None
    try:
        results = dbClass.query_get("SELECT * FROM cross_block.relations WHERE input_address = %s", (addr,))
    except:
        print("Problem retrieving Shapeshift Addresses from DB")
        traceback.print_exc()
    return results


def delete_all_data():
    """ Deletes all found data by the tool """
    dbClass.query("TRUNCATE TABLE exchanges")


def delete_all_scraper_data():
    """ Deletes all found data by the scraper """
    dbClass.query("TRUNCATE TABLE scraper_second")


def closeConnection():
    """ Called when program stops """
    print "Program stopped!"