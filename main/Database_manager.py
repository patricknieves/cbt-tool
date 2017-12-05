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
                "amount_from float DEFAULT NULL,"
                "amount_to float DEFAULT NULL,"
                "fee_from float DEFAULT NULL,"
                "fee_to float DEFAULT NULL,"
                "fee_exchange float DEFAULT NULL,"
                "address_from varchar(120) DEFAULT NULL,"
                "address_to varchar(120) DEFAULT NULL,"
                "hash_from varchar(120) DEFAULT NULL,"
                "hash_to varchar(120) DEFAULT NULL,"
                "time_from datetime DEFAULT NULL,"
                "time_to datetime DEFAULT NULL,"
                "dollarvalue_from float DEFAULT NULL,"
                "dollarvalue_to float DEFAULT NULL,"
                "exchanger varchar(120) DEFAULT NULL,"
                "PRIMARY KEY (id))")

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
                    time_to,
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
            "time_to,"
            "dollarvalue_from,"
            "dollarvalue_to,"
            "exchanger"
            ") "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
             time_to,
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


# Delete all found exchanges in DB
def delete_all_data():
    cur.execute("TRUNCATE TABLE exchanges")


def closeConnection():
    print "Program stopped!"
    db.close()