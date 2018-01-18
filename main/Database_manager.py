import MySQLdb
import atexit
import traceback


def create_database():
    db = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017")
    cur = db.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS cross_block")
    db.close()


def initialize_db():
    create_database()
    global db
    db = MySQLdb.connect(host="localhost", user="root", passwd="Sebis2017", db="cross_block")
    global cur
    cur = db.cursor()
    atexit.register(closeConnection)


def create_table_exchanges():
    cur.execute("CREATE TABLE IF NOT EXISTS exchanges ("
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
    cur.execute("CREATE TABLE IF NOT EXISTS scraper ("
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
    cur.execute("CREATE TABLE IF NOT EXISTS shapeshift_addr_btc ("
                "id int(11) NOT NULL AUTO_INCREMENT,"
                "address varchar(120) DEFAULT NULL,"
                "PRIMARY KEY (id),"
                "UNIQUE INDEX address_UNIQUE (address ASC))")

def insert_shapeshift_address_btc(shapeshift_address):
    try:
        cur.execute(
            "INSERT IGNORE INTO shapeshift_addr_btc (address) VALUES (%s)", shapeshift_address)
        db.commit()
    except:
        print("Problem saving Shapeshift Address: "
              "Address: " + str(shapeshift_address))
        traceback.print_exc()
        db.rollback()

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
    try:
        cur.execute(
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
        db.commit()
    except:
        print("Problem saving Exchange: "
              "hash_from: " + str(hash_from) + " hash_to: " + str(hash_to))
        traceback.print_exc()
        db.rollback()


def insert_shapeshift_exchange(currency_from,
                               currency_to,
                               amount_from,
                               time_exchange,
                               fee_exchange,
                               dollarvalue_from,
                               dollarvalue_to
                               ):
    try:
        cur.execute(
            "INSERT INTO scraper ("
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
        db.commit()
        return cur.lastrowid
    except:
        print("Problem saving Transaction")
        traceback.print_exc()
        db.rollback()

def get_all_shapeshift_addresses_btc():
    standardized_array = []
    try:
        cur.execute("SELECT * FROM cross_block.shapeshift_addr_btc")
        results = cur.fetchall()
        for row in results:
            standardized_array.append(row[1])
    except:
        print("Problem retrieving Shapeshift Addresses from DB")
        traceback.print_exc()
    return list(standardized_array)

def get_shapeshift_exchanges_by_currency(currency):
    standardized_dict = []
    try:
        cur.execute("SELECT * FROM cross_block.scraper WHERE currency_from = %s AND amount_to IS NULL", currency)
        results = cur.fetchall()
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
    try:
        cur.execute(
            "UPDATE scraper SET  "
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
        db.commit()
    except:
        print("Problem updating found Transaction with id: " + str(id))
        traceback.print_exc()
        db.rollback()


def update_shapeshift_exchange_corresponding_tx(time_to, time_block_to, fee_to, block_nr_to, id):
    try:
        cur.execute(
            "UPDATE scraper SET  "
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
        db.commit()
    except:
        print("Problem updating found Transaction with id: " + str(id))
        traceback.print_exc()
        db.rollback()


# Delete all found exchanges in DB
def delete_all_data():
    cur.execute("TRUNCATE TABLE exchanges")


# Delete all found shapeshift exchanges in DB
def delete_all_scraper_data():
    cur.execute("TRUNCATE TABLE scraper")


def closeConnection():
    print "Program stopped!"
    db.close()