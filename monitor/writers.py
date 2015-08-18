import abc


class IBaseWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, url, response):
        pass

    def get_response_data(self, response):
        return {
            'code': response.code,
            'time': response.request_time,
            'headers': response.headers
        }


class MemoryWriter(IBaseWriter):

    def __init__(self, *args, **kwargs):
        self.url_status = {}

    def write(self, url, response):
        data = self.get_response_data(response=response)
        self.url_status[url] = data
