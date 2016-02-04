import abc

from tormon.core import settings
from tormon.models import resources_from_dicts


class IBaseReader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        pass


class ConfigReader(IBaseReader):

    def read(self, *args, **kwargs):
        return resources_from_dicts(settings.get(u'resources'))
