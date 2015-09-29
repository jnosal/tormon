import os
import time
import signal
import logging

import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient

from tormon.monitor import client
from tormon.api import urls as api_urls
from tormon.web import urls as web_urls


root = lambda *x: os.path.join(os.path.dirname(__file__), u'../', *x)
APP_ROOT = root()
STATIC_ROOT = root(u'static')
TEMPLATE_ROOT = root(u'templates')
BLOCKING_THRESHOLD = 0.2

AsyncHTTPClient.configure(u"tornado.curl_httpclient.CurlAsyncHTTPClient")

define(u"reader", default=u"file", help=u"Name of reader that's used to provide urls")
define(u"writer", default=u"memory", help=u"Name of writer that's persisting urls")
define(u'filename', default=None, help=u"Path to file, required by file reader")
define(u"host", default=u"localhost")
define(u"port", default=8081, type=int)
define(u"debug", default=True, type=bool)
define(u"concurrency", default=0, type=int)


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


def main():
    options.parse_command_line()

    monitor = client.WebMonitor(
        reader=options[u'reader'],
        writer=options[u'writer'],
        concurrency=options[u'concurrency'],
        filename=options[u'filename'],
    )
    application = MonitorWebApplication(
        monitor_instance=monitor,
        debug=options[u'debug'],
        static_path=STATIC_ROOT,
        template_path=TEMPLATE_ROOT
    )
    server = HTTPServer(application)

    logging.info(u"Starting APP-MONITOR on {0}:{1}.".format(
        options[u'host'], options[u'port']
    ))

    shutdown_handler = lambda sig, frame: shutdown(server, monitor)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if options[u'debug']:
        logging.info(u"Setting blocking threshold to: {}".format(
            BLOCKING_THRESHOLD
        ))
        IOLoop.instance().set_blocking_log_threshold(BLOCKING_THRESHOLD)

    server.listen(options[u'port'], options[u'host'])
    monitor.start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()