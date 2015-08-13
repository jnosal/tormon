import abc


class IBaseWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, url, response):
        pass


class MemoryWriter(IBaseWriter):

    def __init__(self, *args, **kwargs):
        self.url_status = {}

    def write(self, url, response):
        self.url_status[url] = response
