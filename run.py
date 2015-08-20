import time
import signal
import logging

import tornado.ioloop
import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient

import settings
import environment
from monitor import client
from api import urls as api_urls
from web import urls as web_urls


AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

BLOCKING_THRESHOLD = 0.5
define("reader", default="file", help="Name of reader that's used to provide urls")
define("writer", default="memory", help="Name of writer that's persisting urls")
define('filename', default=None, help="Path to file, required by file reader")
define("host", default="localhost")
define("port", default=8081, type=int)
define("debug", default=True, type=bool)


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
    options.parse_command_line()

    monitor = client.WebMonitor(
        reader=options['reader'],
        writer=options['writer'],
        filename=options['filename']
    )
    application = MonitorWebApplication(
        monitor_instance=monitor,
        debug=options['debug'],
        static_path=settings.STATIC_ROOT,
        template_path=settings.TEMPLATE_ROOT
    )
    server = HTTPServer(application)

    logging.info(u"Starting APP-MONITOR on {0}:{1}.".format(
        options['host'], options['port']
    ))

    shutdown_handler = lambda sig, frame: shutdown(server, monitor)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if options['debug']:
        logging.info(u"Setting blocking threshold to: {}".format(
            BLOCKING_THRESHOLD
        ))
        IOLoop.instance().set_blocking_log_threshold(BLOCKING_THRESHOLD)

    server.listen(options['port'], options['host'])
    monitor.start()
    IOLoop.instance().start()