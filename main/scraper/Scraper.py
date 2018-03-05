from main import Database_manager
import time
import Finder
from threading import Thread
from Shapeshift import Shapeshift


def main():
    setup_db()
    #Database_manager.delete_all_scraper_data()
    t = Thread(target=Finder.find, args=())
    t.start()
    get_shapeshift_exchanges_limitless()


def setup_db():
    Database_manager.create_database()
    Database_manager.initialize_db()
    Database_manager.create_table_scraper()


def get_shapeshift_exchanges_limitless():
    shapeshift_manager = Shapeshift()
    while True:
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)


def get_shapeshift_exchanges(runtime_in_sec):
    shapeshift_manager = Shapeshift()
    start_time = time.time()
    elapsed_time = 0
    # Run a whole day
    while elapsed_time < runtime_in_sec:
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration.total_seconds()/2
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)
        elapsed_time = time.time() - start_time


def get_shapeshift_exchanges_instant(runtime_in_sec):
    shapeshift_manager = Shapeshift()
    start_time = time.time()
    elapsed_time = 0

    # Run a whole day
    while elapsed_time < runtime_in_sec:
        start_time_loop = time.time()
        shapeshift_manager.get_new_exchanges()
        duration_to_wait = shapeshift_manager.duration.total_seconds()/2
        t = Thread(target=Finder.find_exchange_data, args=())
        #t = Thread(target=find_exchange_data, args=(new_exchanges,))
        t.start()
        elapsed_time_loop = time.time() - start_time_loop
        if elapsed_time_loop < duration_to_wait:
            print ("Done! Wait " + str(duration_to_wait - elapsed_time_loop) + " seconds")
            time.sleep(duration_to_wait - elapsed_time_loop)
        elapsed_time = time.time() - start_time



if __name__ == "__main__": main()