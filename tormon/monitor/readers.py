import abc
import logging


class IBaseReader(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        pass


class TextFileReader(IBaseReader):

    def __init__(self, *args, **kwargs):
        self.filename = kwargs.get(u'filename')

    def read(self, *args, **kwargs):
        try:
            with open(self.filename, u'r') as f:
                return iter(f.read().splitlines())
        except IOError:
            logging.error(u"Can't read file: {}.".format(self.filename))
            return []
