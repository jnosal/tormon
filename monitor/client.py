import abc
import logging
import random
import time

import tornado.gen
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient

from . import exceptions
from . import readers
from . import writers
from . import utils


class IBaseMonitor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self.client = None
        self.reader_instance = None
        self.writer_instance = None

    @abc.abstractmethod
    def get_reader_instance(self):
        pass

    @abc.abstractmethod
    def get_writer_instance(self):
        pass

    @abc.abstractmethod
    def monitor(self, url):
        pass

    def get_client_instance(self):
        return AsyncHTTPClient(max_clients=1000)

    @tornado.gen.coroutine
    def iter_urls(self, *args, **kwargs):
        data = yield tornado.gen.Task(self.writer_instance.iter_data)
        raise tornado.gen.Return(data)

    @tornado.gen.coroutine
    def get_info(self, url):
        data = yield tornado.gen.Task(self.writer_instance.get_info, url)
        raise tornado.gen.Return(data)

    @tornado.gen.coroutine
    def get_stats(self):
        data = yield tornado.gen.Task(self.writer_instance.get_stats)
        raise tornado.gen.Return(data)

    def start(self, *args, **kwargs):
        self.reader_instance = self.get_reader_instance()
        self.writer_instance = self.get_writer_instance()
        self.client = self.get_client_instance()

        for url in self.reader_instance.read():
            logging.info(u'{} - starting monitoring'.format(url))
            self.monitor(url=url)

    def stop(self, *args, **kwargs):
        pass


class WebMonitor(IBaseMonitor):

    def __init__(self, reader='file', writer='memory', *args, **kwargs):
        super(WebMonitor, self).__init__(*args, **kwargs)
        self.reader = reader
        self.writer = writer
        self.kwargs = kwargs

    def get_reader_instance(self):
        class_map = {
            utils.FILE_READER: readers.TextFileReader,
        }

        try:
            Reader = class_map[self.reader]
            return Reader(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate reader. Allowed: {0}".format(
                u", ".join(utils.ALLOWED_READERS)
            )
            raise exceptions.ConfigurationException(msg)

    def get_writer_instance(self):
        class_map = {
            utils.MEMORY_WRITER: writers.MemoryWriter,
            utils.REDIS_WRITER: writers.RedisWriter
        }

        try:
            Writer = class_map[self.writer]
            return Writer(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate writer. Allowed: {0}".format(
                u", ".join(utils.ALLOWED_WRITERS)
            )
            raise exceptions.ConfigurationException(msg)

    @tornado.gen.coroutine
    def monitor(self, url):
        logging.info(u"Sending request to: {}".format(url))
        response = yield self.client.fetch(url, method='HEAD')
        self.writer_instance.write(url=url, response=response)

        cb = lambda: self.monitor(url=url)
        deadline = time.time() + random.randint(0, 15)
        ioloop.IOLoop.instance().add_timeout(deadline=deadline, callback=cb)

    def stop(self, *args, **kwargs):
        pass