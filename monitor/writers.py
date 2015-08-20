import abc
import logging
from itertools import izip
from datetime import datetime

import tornado.gen

from api import utils


class IBaseWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def iter_data(self):
        pass

    @abc.abstractmethod
    def write(self, url, response):
        pass

    @abc.abstractmethod
    def get_info(self, url):
        pass

    @abc.abstractmethod
    def get_stats(self):
        pass

    @property
    def updated_at(self):
        return datetime.now()

    def get_response_data(self, response):
        return {
            'code': response.code,
            'time': response.request_time,
            'headers': response.headers,
            'updated_at': self.updated_at
        }


class MemoryWriter(IBaseWriter):

    def __init__(self, *args, **kwargs):
        self.url_status = {}

    def write(self, url, response):
        data = self.get_response_data(response=response)
        self.url_status[url] = data

    @tornado.gen.coroutine
    def iter_data(self):
        data = self.url_status
        raise tornado.gen.Return(data.iteritems())

    @tornado.gen.coroutine
    def get_info(self, url):
        data = self.url_status[url]
        raise tornado.gen.Return(data)

    @tornado.gen.coroutine
    def get_stats(self):
        data = yield tornado.gen.Task(self.iter_data)
        urls = [
            url for url, _ in data
        ]

        stats = {
            'total_monitored': len(urls),
            'urls': urls
        }
        raise tornado.gen.Return(stats)


class RedisWriter(IBaseWriter):
    KEY_PREFIX = u'tormon-'

    def __init__(self, *args, **kwargs):
        import redis
        self.r = redis.StrictRedis()

    def key(self, base):
        return u"{}{}".format(self.KEY_PREFIX, base)

    @tornado.gen.coroutine
    def iter_data(self):
        match = u"{}*".format(self.KEY_PREFIX)
        count = None
        results = {}

        keys = [
            key for
            key in self.r.scan_iter(match=match, count=count)
        ]

        values = self.r.mget(keys)

        keys = map(lambda x: x.replace(self.KEY_PREFIX, u''), keys)
        values = map(lambda x: utils.json_loads(x), values)
        results.update(dict(izip(keys, values)))

        raise tornado.gen.Return(results.iteritems())

    @tornado.gen.coroutine
    def write(self, url, response):
        data = self.get_response_data(response=response)
        json_data = utils.json_dumps(data)
        self.r.set(self.key(url), json_data)

    @tornado.gen.coroutine
    def get_info(self, url):
        key = self.key(url)
        data = self.r.get(key)
        if not data:
            raise KeyError(u"Key: {} does not exist in db".format(key))
        raise tornado.gen.Return(utils.json_loads(data))

    @tornado.gen.coroutine
    def get_stats(self):
        data = yield tornado.gen.Task(self.iter_data)
        urls = [
            url for url, _ in data
        ]

        stats = {
            'total_monitored': len(urls),
            'urls': urls
        }
        raise tornado.gen.Return(stats)