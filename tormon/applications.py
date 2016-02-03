import tornado.web

from tormon.api import urls as api_urls
from tormon.web import urls as web_urls


class MonitorWebApplication(tornado.web.Application):

    def __init__(self, monitor_instance, **kwargs):
        handlers = self.get_handlers()
        self.monitor = monitor_instance
        tornado.web.Application.__init__(self, handlers, **kwargs)

    def get_handlers(self):
        return api_urls.urlpatterns + web_urls.urlpatterns
