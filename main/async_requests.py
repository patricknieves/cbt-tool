from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue, Empty
import requests
import time
import Currency_apis
import threading

class Async_requester(object):

    def __init__(self):
        self.concurrent = 200
        self.all_blocks = []
        self.request_data_array = []
        self.q = Queue(self.concurrent * 2)


    def doWork(self, stop_event):
        while not stop_event.wait(0):
            try:
                block_info = self.q.get(timeout=0)
                if block_info:
                    block = Currency_apis.get_block_by_number(block_info["currency"], block_info["number"])
                    if block:
                        self.all_blocks.append(block)
                    self.q.task_done()
            except Empty:
                continue

    def get_multiple_blocks(self, currency, start_block, number_of_blocks):
        start = time.time()
        self.all_blocks = []
        try:
            for i in range(number_of_blocks):
                self.q.put({"currency": currency, "number": start_block - i})
            self.q.join()
        except KeyboardInterrupt:
            sys.exit(1)
        print("Duration: " + str(time.time() - start))
        self.all_blocks.sort(key=lambda x: x[0]["block_nr"], reverse=True)
        return self.all_blocks

    def add_request_data(self, currency, start_block, number_of_blocks):
        self.request_data_array.append({"currency": currency, "start_block": start_block, "number_of_blocks": number_of_blocks})

    def get_multiple_blocks_all_currencies(self):
        start = time.time()
        self.all_blocks = []

        pill2kill = threading.Event()
        def thread_gen(pill2kill):
            for i in range(self.concurrent):
                t = Thread(target=self.doWork, args=(pill2kill,))
                t.daemon = True
                yield t
        threads = list(thread_gen(pill2kill))
        map(threading.Thread.start, threads)

        try:
            for currency_blocks in self.request_data_array:
                for i in range(currency_blocks["number_of_blocks"]):
                    self.q.put({"currency": currency_blocks["currency"], "number": currency_blocks["start_block"] - i})
            self.q.join()
        except KeyboardInterrupt:
            sys.exit(1)
        self.request_data_array = []

        pill2kill.set()
        map(threading.Thread.join, threads)

        print("Duration total: " + str(time.time() - start))
        self.all_blocks.sort(key=lambda x: x[0]["block_nr"], reverse=True)
        return self.all_blocks

def main_old():
    ar = Async_requester()
    print(threading.active_count())
    result = ar.get_multiple_blocks("BTC", 499026, 6)
    print(threading.active_count())
    result = ar.get_multiple_blocks("ETH", 4724187, 4*60)
    print(threading.active_count())
    print ("finish")

def main():
    ar = Async_requester()
    print(threading.active_count())
    ar.add_request_data("BTC", 499026, 6)
    ar.add_request_data("ETH", 4724187, 4*60)
    ar.get_multiple_blocks_all_currencies()
    print(threading.active_count())
    print ("finish")


if __name__ == "__main__": main()
