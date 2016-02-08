import os
import logging
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), u'..'))

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient

from tormon import core
from tormon.core import utils

root = lambda *x: os.path.join(os.path.dirname(__file__), u'../', *x)
APP_ROOT = root()
STATIC_ROOT = root(u'static')
TEMPLATE_ROOT = root(u'templates')
BLOCKING_THRESHOLD = 0.2

try:
    AsyncHTTPClient.configure(u"tornado.curl_httpclient.CurlAsyncHTTPClient")
except ImportError:
    pass

define(u'app', default=u'', type=str, help=u'Pusher application to run')
define(u'monitor', default=u'', type=str, help=u'Pusher application to run')
define(u"writer", default=u'memory', help=u"Name of writer that's persisting urls")
define(
    u"reader",
    default=u"config",
    help=u"Name reader for getting urls (by default, they're taken from config file)."
)
define(u'handler', default=u'log', help=u"Name of handler in case resource is failing")
define(u'config', type=str, default=None, help=u'Path to yaml file')
define(u"host", default=u"localhost")
define(u"port", default=8081, type=int)
define(u"debug", default=False, type=bool)
define(u"concurrency", default=0, type=int)


def setup_application(monitor_instance):
    ApplicationClass = utils.load_app(options[u'app'])
    return ApplicationClass(
        monitor_instance=monitor_instance,
        debug=options[u'debug'],
        static_path=STATIC_ROOT,
        template_path=TEMPLATE_ROOT
    )


def setup_monitor():
    MonitorClass = utils.load_monitor(options[u'monitor'])
    return MonitorClass(
        reader=options[u'reader'],
        writer=options[u'writer'],
        handler=options[u'handler'],
        concurrency=options[u'concurrency']
    )


def validate_options():
    if not options[u'config']:
        logging.error(u"Config is missing")
        sys.exit(1)


def main():
    options.parse_command_line()
    validate_options()
    core.settings.import_config(options[u'config'])

    monitor = setup_monitor()
    application = setup_application(monitor_instance=monitor)
    server = HTTPServer(application)

    logging.info(u"Starting APP-MONITOR on {0}:{1}.".format(
        options[u'host'], options[u'port']
    ))
    utils.register_shutdown_handlers(server, monitor)

    if options[u'debug']:
        logging.info(u"Setting blocking threshold to: {}".format(
            BLOCKING_THRESHOLD
        ))
        IOLoop.instance().set_blocking_log_threshold(BLOCKING_THRESHOLD)

    server.listen(options[u'port'], options[u'host'])
    monitor.start()
    IOLoop.instance().start()


if __name__ == u'__main__':
    main()
