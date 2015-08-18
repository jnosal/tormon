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


class MonitorWebApplication(tornado.web.Application):

    def __init__(self, **kwargs):
        handlers = []
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

    application = MonitorWebApplication(debug=settings.DEBUG)
    server = HTTPServer(application)

    logging.info(u"Starting APP-MONITOR on {0}:{1}.".format(
        settings.HOST, settings.PORT
    ))
    server.listen(settings.PORT, settings.HOST)

    monitor = client.WebMonitor(
        reader='file', writer='memory',
        filename=u'/tmp/a.txt'
    )
    monitor.start()

    shutdown_handler = lambda sig, frame: shutdown(server, monitor)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    IOLoop.instance().start()