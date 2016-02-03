import logging
import importlib
import signal
import time

from tormon import applications
from tormon.monitor import client

from tornado.ioloop import IOLoop


def load_app(name, default=None):
    default = default or applications.MonitorWebApplication
    return load_component(name, default)


def load_monitor(name, default=None):
    default = default or client.WebMonitor
    return load_component(name, default)


def load_component(name, default):
    loaded = default

    if name:
        try:
            components = name.split(u'.')
            module_name = u".".join(components[:-1])
            module = importlib.import_module(module_name)
            loaded = getattr(module, components[-1])
        except AttributeError:
            logging.error(u"Error loading: {0}. Switching to: {1}.".format(
                name, default.__name__
            ))

    logging.info(u"Loaded component: {0}".format(loaded.__name__))
    return loaded


def shutdown(server_instance, *args):
    ioloop_instance = IOLoop.instance()
    logging.info(u'Shutting down gracefully.')

    server_instance.stop()

    for component in args:
        component.stop()

    def finalize():
        ioloop_instance.stop()
        logging.info(u'Shut down.')

    ioloop_instance.add_timeout(time.time() + 1.5, finalize)


def register_shutdown_handlers(server, *args):
    shutdown_handler = lambda sig, frame: shutdown(server, *args)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
