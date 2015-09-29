import abc
import logging
import random
import time

import tornado.gen
import tornado.ioloop
import tornado.locks
from tornado.httpclient import AsyncHTTPClient, HTTPError

from . import exceptions
from . import readers
from . import utils
from . import writers


HTTP_MAX_CLIENTS = 1000
CONNECT_TIMEOUT = 10
REQUEST_TIMEOUT = 1000

READER_MAP = {
    utils.FILE_READER: readers.TextFileReader,
}

WRITER_MAP = {
    utils.MEMORY_WRITER: writers.MemoryWriter,
    utils.REDIS_WRITER: writers.RedisWriter
}


class IBaseMonitor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, reader=u'file', writer=u'memory', *args, **kwargs):
        self.reader = reader
        self.writer = writer
        self.client = None
        self.primitive = None
        self.reader_instance = None
        self.writer_instance = None
        self.concurrency = kwargs.get(u'concurrency', 0)
        self.reader_map = kwargs.get(u'reader_map', READER_MAP)
        self.writer_map = kwargs.get(u'writer_map', WRITER_MAP)

    def get_concurrency_primitive(self):
        return tornado.locks.Semaphore(self.concurrency)

    def get_reader_instance(self):
        try:
            ReaderClass = self.reader_map[self.reader]
            return ReaderClass(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate reader. Allowed: {0}".format(
                u", ".join(self.reader_map.iterkeys())
            )
            raise exceptions.ConfigurationException(msg)

    def get_writer_instance(self):
        try:
            WriterClass = self.writer_map[self.writer]
            return WriterClass(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate writer. Allowed: {0}".format(
                u", ".join(self.reader_map.iterkeys())
            )
            raise exceptions.ConfigurationException(msg)

    def setup(self):
        if self.concurrency:
            logging.info(u"Concurrency set to {0}".format(self.concurrency))
            self.primitive = self.get_concurrency_primitive()

        self.reader_instance = self.get_reader_instance()
        self.writer_instance = self.get_writer_instance()
        self.client = self.get_client_instance()

    @abc.abstractmethod
    def monitor(self, url):
        pass

    def get_client_instance(self):
        return AsyncHTTPClient(max_clients=HTTP_MAX_CLIENTS)

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
        self.setup()

        for url in self.reader_instance.read():
            logging.info(u'{} - starting monitoring'.format(url))
            self.monitor(url=url)

    def stop(self, *args, **kwargs):
        logging.info(u"Stopping {}.".format(self.__class__.__name__))


class WebMonitor(IBaseMonitor):

    def __init__(self, *args, **kwargs):
        super(WebMonitor, self).__init__(*args, **kwargs)
        self.kwargs = kwargs

    @tornado.gen.coroutine
    def monitor_url(self, url):
        now = time.time()
        try:
            response = yield self.client.fetch(
                url, method=u'HEAD',
                request_timeout=REQUEST_TIMEOUT,
                connect_timeout=CONNECT_TIMEOUT
            )
            self.writer_instance.write_response(url=url, response=response)
        except HTTPError as e:
            logging.error(u"[{}] {}".format(url, str(e)))
            self.writer_instance.write_error(url=url, error=e)

        deadline = now + random.randint(5, 15)

        callback = lambda: self.monitor(url=url)
        tornado.ioloop.IOLoop.instance().add_timeout(
            deadline=deadline,
            callback=callback
        )

    @tornado.gen.coroutine
    def monitor(self, url):
        if self.primitive:
            with (yield self.primitive.acquire()):
                self.monitor_url(url=url)
        else:
            self.monitor_url(url=url)