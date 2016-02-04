import abc
import logging

from tormon.core import settings


class IBaseReader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        pass


class ConfigReader(IBaseReader):

    def read(self, *args, **kwargs):
        return iter(settings.get(u'urls'))


class TextFileReader(IBaseReader):
    """
        Old reader, which reads url list from provided file contents.
        Use in favour of config reader which can be used to provide urls
        among other parameters.
    """
    def __init__(self, *args, **kwargs):
        super(TextFileReader, self).__init__(*args, **kwargs)
        self.filename = kwargs.get(u'filename', settings.get(u'filename', None))
        if not self.filename:
            raise AttributeError(u"Filename missing.")

    def read(self, *args, **kwargs):
        try:
            with open(self.filename, u'r') as f:
                return iter(f.read().splitlines())
        except IOError:
            logging.error(u"Can't read file: {}.".format(self.filename))
            return []
