from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue
import requests
import time
import Currency_apis
import threading

class Async_requester(object):

    def __init__(self):
        self.concurrent = 200
        self.all_blocks = []
        self.q = Queue(self.concurrent * 2)
        for i in range(self.concurrent):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()

    def doWork(self):
        while True:
            block_info = self.q.get()
            block = Currency_apis.get_block_by_number(block_info["currency"], block_info["number"])
            if block:
                self.all_blocks.append(block)
            self.q.task_done()

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

def main():
    ar = Async_requester()
    print(threading.active_count())
    result = ar.get_multiple_blocks("BTC", 499026, 6)
    print(threading.active_count())
    result = ar.get_multiple_blocks("ETH", 4724187, 4*60)
    print(threading.active_count())
    print ("finish")

if __name__ == "__main__": main()
