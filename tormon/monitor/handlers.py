import abc
import logging

DEFAULT_ALGORITHM = u''


class IBaseHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        logging.info(u'Initializing handler: {0}'.format(
            self.__class__.__name__
        ))
        self.algorithm = kwargs.get(u'algorithm', DEFAULT_ALGORITHM)

    @abc.abstractmethod
    def notify(self, *args, **kwargs):
        pass


class SmtpHandler(IBaseHandler):

    def notify(self, *args, **kwargs):
        pass


class LogHandler(IBaseHandler):

    def notify(self, *args, **kwargs):
        pass


class ApiCallHandler(IBaseHandler):

    def notify(self, *args, **kwargs):
        pass

