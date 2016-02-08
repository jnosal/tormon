import abc
import logging
import random
import time

import tornado.gen
import tornado.ioloop
import tornado.locks
from tornado.httpclient import AsyncHTTPClient, HTTPError

from . import exceptions
from . import handlers
from . import readers
from . import writers


DEFAULT_HEALTHCHECK_HTTP_METHOD = u'HEAD'
HTTP_MAX_CLIENTS = 1000
CONNECT_TIMEOUT = 10
RANDOM_RANGE = (1, 2)
REQUEST_TIMEOUT = 1000

HANDLER_LOG = u'log'
HANDLER_EMAIL = u'email'
HANDLER_API_CALL = u'api-call'
READER_CONFIG = u'config'
WRITER_MEMORY = u'memory'
WRITER_REDIS = u'redis'


READER_MAP = {
    READER_CONFIG: readers.ConfigReader
}

WRITER_MAP = {
    WRITER_MEMORY: writers.MemoryWriter,
    WRITER_REDIS: writers.RedisWriter
}

HANDLER_MAP = {
    HANDLER_API_CALL: handlers.ApiCallHandler,
    HANDLER_LOG: handlers.LogHandler,
    HANDLER_EMAIL: handlers.SmtpHandler
}


class IBaseMonitor(object):
    __metaclass__ = abc.ABCMeta
    LOG_INFO = u"[{0}]"

    def __init__(self, reader=READER_CONFIG, writer=WRITER_MEMORY,
                 handler=HANDLER_LOG, *args, **kwargs):
        self.reader = reader
        self.writer = writer
        self.handler = handler
        self.client = None
        self.primitive = None
        self.reader_instance = None
        self.writer_instance = None
        self.handler_instance = None
        self.concurrency = kwargs.get(u'concurrency', 0)
        self.reader_map = kwargs.get(u'reader_map', READER_MAP)
        self.writer_map = kwargs.get(u'writer_map', WRITER_MAP)
        self.handler_map = kwargs.get(u'handler_map', HANDLER_MAP)
        self.kwargs = kwargs

    def get_concurrency_primitive(self):
        return tornado.locks.Semaphore(self.concurrency)

    def get_reader_instance(self):
        try:
            ReaderClass = self.reader_map[self.reader]
            return ReaderClass(**self.kwargs)
        except KeyError as e:
            msg = u"Inappropriate reader. Allowed: {0}".format(
                u", ".join(self.reader_map.iterkeys())
            )
            raise exceptions.ConfigurationException(msg)
        except AttributeError as e:
            msg = u"Inappropriate params. Allowed: {0}".format(
                str(e)
            )
            raise exceptions.ConfigurationException(msg)

    def get_writer_instance(self):
        try:
            WriterClass = self.writer_map[self.writer]
            return WriterClass(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate writer. Allowed: {0}".format(
                u", ".join(self.writer_map.iterkeys())
            )
            raise exceptions.ConfigurationException(msg)

    def get_handler_instance(self):
        try:
            HandlerClass = self.handler_map[self.handler]
            return HandlerClass(**self.kwargs)
        except KeyError:
            msg = u"Inappropriate handler. Allowed: {0}".format(
                u", ".join(self.handler_map.iterkeys())
            )
            raise exceptions.ConfigurationException(msg)

    def setup(self):
        if self.concurrency:
            logging.info(u"Concurrency set to {0}".format(self.concurrency))
            self.primitive = self.get_concurrency_primitive()

        self.reader_instance = self.get_reader_instance()
        self.writer_instance = self.get_writer_instance()
        self.handler_instance = self.get_handler_instance()
        self.client = self.get_client_instance()

    def get_client_instance(self):
        return AsyncHTTPClient(max_clients=HTTP_MAX_CLIENTS)

    @tornado.gen.coroutine
    def iter_resources(self, *args, **kwargs):
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

        for resource in self.reader_instance.read():
            logging.info(u'{} - starting monitoring'.format(resource))
            self.monitor(resource=resource)

    def stop(self, *args, **kwargs):
        logging.info(u"Stopping {}.".format(self.__class__.__name__))

    def _reschedule_monitor(self, resource):
        deadline = time.time() + random.randint(*RANDOM_RANGE)
        tornado.ioloop.IOLoop.instance().add_timeout(
            deadline=deadline,
            callback=lambda: self.monitor(resource=resource)
        )

    @tornado.gen.coroutine
    def monitor(self, resource):
        """
        Should be called periodically by monitor_resource_handler
        See HealthcheckMonitor
        """
        logging.debug(self.LOG_INFO.format(resource))

        if self.primitive:
            with (yield self.primitive.acquire()):
                self.monitor_resource_handler(resource=resource)
        else:
            self.monitor_resource_handler(resource=resource)

    @abc.abstractmethod
    def monitor_resource_handler(self, resource):
        pass


class HealthCheckMonitor(IBaseMonitor):
    LOG_INFO = u"[{0}] - Healthchecking"

    def __init__(self, *args, **kwargs):
        super(HealthCheckMonitor, self).__init__(*args, **kwargs)
        self.kwargs = kwargs

    @tornado.gen.coroutine
    def monitor_resource_handler(self, resource):
        try:
            response = yield self.client.fetch(
                resource.url,
                method=DEFAULT_HEALTHCHECK_HTTP_METHOD,
                request_timeout=REQUEST_TIMEOUT,
                connect_timeout=CONNECT_TIMEOUT
            )
            self.writer_instance.write_response(
                resource=resource,
                response=response
            )
        except HTTPError as e:
            self.writer_instance.write_error(
                resource=resource, error=e
            )

        self._reschedule_monitor(resource)


class SmokeTestMonitor(IBaseMonitor):
    LOG_INFO = u"[{0}] - Smoketesting"

    def __init__(self, *args, **kwargs):
        super(SmokeTestMonitor, self).__init__(*args, **kwargs)
        self.kwargs = kwargs

    @tornado.gen.coroutine
    def monitor_resource_handler(self, resource):
        self._reschedule_monitor(resource)

