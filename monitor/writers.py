import abc
from datetime import datetime


class IBaseWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __iter__(self):
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

    def __iter__(self):
        return self.url_status.iteritems()

    def write(self, url, response):
        data = self.get_response_data(response=response)
        self.url_status[url] = data

    def get_info(self, url):
        return self.url_status[url]

    def get_stats(self):
        return {
            'total_monitored': len(self.url_status),
            'urls': [
                url for url, _ in self
            ]
        }