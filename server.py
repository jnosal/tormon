import time
import signal
import logging

import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line

import settings
from monitor import client
from api import urls as api_urls
from web import urls as web_urls


class MonitorWebApplication(tornado.web.Application):

    def __init__(self, monitor_instance, **kwargs):
        handlers = api_urls.urlpatterns + web_urls.urlpatterns
        self.monitor = monitor_instance
        tornado.web.Application.__init__(self, handlers, **kwargs)


def shutdown(server_instance, monitor_instance):
    ioloop_instance = IOLoop.instance()
    logging.info(u'Stopping APP-MONITOR gracefully.')

    server_instance.stop()
    monitor_instance.stop()

    def finalize():
        ioloop_instance.stop()
        logging.info(u'APP-MONITOR stopped.')

    ioloop_instance.add_timeout(time.time() + 1.5, finalize)


if __name__ == '__main__':
    parse_command_line()

    monitor = client.WebMonitor(
        reader='file',
        writer='memory',
        filename=u'/tmp/a.txt'
    )
    application = MonitorWebApplication(
        monitor_instance=monitor,
        debug=settings.DEBUG,
        static_path=settings.STATIC_ROOT,
        template_path=settings.TEMPLATE_ROOT
    )
    server = HTTPServer(application)

    logging.info(u"Starting APP-MONITOR on {0}:{1}.".format(
        settings.HOST, settings.PORT
    ))
    server.listen(settings.PORT, settings.HOST)

    monitor.start()

    shutdown_handler = lambda sig, frame: shutdown(server, monitor)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    IOLoop.instance().start()