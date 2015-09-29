import tornado.web
import tornado.gen

from . import utils


class BaseApiHandler(tornado.web.RequestHandler):

    def response(self, data, code=200):
        if code != 200:
            # if something went wrong, we include returned HTTP code in the
            # JSON response
            data['status'] = code

        self.write(utils.json_dumps(data) + "\n")
        self.set_status(code)

    def error(self, message, code=500):
        self.response({'message': message}, code)

    def options(self, *args, **kwargs):
        pass


class StatsHandler(BaseApiHandler):

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        stats = yield self.application.monitor.get_stats()
        self.response({'stats': stats}, 200)


class UrlsListHandler(BaseApiHandler):

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        data = yield self.application.monitor.iter_urls()
        objects = [
            dict(url=url, response=response)
            for url, response
            in data
        ]
        self.response({'objects': objects}, 200)


class UrlDetailsHandler(BaseApiHandler):

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        url = self.get_argument('url', None)

        try:
            info = yield self.application.monitor.get_info(url)
            self.response({'response': info}, 200)
        except KeyError:
            error = (
                u"Url: {} is not monitored. Perhaps slash is missing"
                u" or is redundant."
            ).format(url)
            self.response({'error': error}, 400)