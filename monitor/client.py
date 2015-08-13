import abc
import time
import logging
import random

import tornado.gen
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient

from . import readers
from . import writers


class IBaseMonitor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_source_instance(self):
        pass

    @abc.abstractmethod
    def get_output_instance(self):
        pass

    @abc.abstractmethod
    def monitor(self, url):
        pass

    def start(self, *args, **kwargs):
        self.reader = self.get_source_instance()
        self.writer = self.get_output_instance()

        for url in self.reader.read():
            logging.info(u'Starting monitor: {}'.format(url))
            self.monitor(url=url)

    def stop(self, *args, **kwargs):
        pass


class WebMonitor(IBaseMonitor):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.client = AsyncHTTPClient()

    def get_source_instance(self):
        return readers.TextFileReader(**self.kwargs)

    def get_output_instance(self):
        return writers.MemoryWriter(**self.kwargs)

    @tornado.gen.engine
    def monitor(self, url):
        logging.info(u"Sending request to {}".format(url))
        response = yield tornado.gen.Task(self.client.fetch, url)
        self.writer.write(url=url, response=response)

        cb = lambda: self.monitor(url=url)
        deadline = time.time() + random.randint(0, 15)
        ioloop.IOLoop.instance().add_timeout(deadline=deadline, callback=cb)

    def stop(self, *args, **kwargs):
        pass