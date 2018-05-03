from urlparse import urlparse
from threading import Thread
import httplib, sys
from Queue import Queue, Empty
import requests
import time
import Currency_apis
import threading

class Async_requester(object):
    """ Class responsible for requesting blocks asynchronously """
    def __init__(self):
        self.concurrent = 200
        self.all_blocks = []
        self.request_data = []
        self.queue = Queue(self.concurrent * 2)


    def do_work(self, stop_event):
        """ Retrieves data from queue and downloads one block """
        while not stop_event.wait(0):
            try:
                block_info = self.queue.get(timeout=0)
                if block_info:
                    block = Currency_apis.get_block_by_number(block_info["currency"], block_info["number"])
                    if block:
                        self.all_blocks.append(block)
                    self.queue.task_done()
            except Empty:
                continue

    def add_request_data(self, currency, start_block, number_of_blocks):
        """ Adds data of the blocks which shall be downloaded. Data contain the currency,
        the block number and the number of blocks which shall be downloaded starting from the given number """
        self.request_data.append({"currency": currency, "start_block": start_block, "number_of_blocks": number_of_blocks})

    def get_multiple_blocks(self):
        """ Executes the downloading process and returns all blocks """
        start = time.time()
        self.all_blocks = []

        pill2kill = threading.Event()
        def thread_gen(pill2kill):
            for i in range(self.concurrent):
                t = Thread(target=self.do_work, args=(pill2kill,))
                t.daemon = True
                yield t
        threads = list(thread_gen(pill2kill))
        map(threading.Thread.start, threads)

        try:
            for currency_blocks in self.request_data:
                for i in range(currency_blocks["number_of_blocks"]):
                    self.queue.put({"currency": currency_blocks["currency"], "number": currency_blocks["start_block"] - i})
            self.queue.join()
        except KeyboardInterrupt:
            sys.exit(1)
        self.request_data = []

        pill2kill.set()
        map(threading.Thread.join, threads)

        self.all_blocks.sort(key=lambda x: x[0]["block_nr"], reverse=True)
        return self.all_blocks
