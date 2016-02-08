import abc
import logging

from tormon.core import settings
from tormon.models import resources_from_dicts


class IBaseReader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        logging.info(u'Initializing reader: {0}'.format(
            self.__class__.__name__
        ))

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        pass


class ConfigReader(IBaseReader):

    def read(self, *args, **kwargs):
        return resources_from_dicts(settings.get(u'resources'))
