import tornado.web

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

    def get(self, *args, **kwargs):
        stats = self.application.monitor.get_stats()
        return self.response({'stats': stats}, 200)


class UrlsListHandler(BaseApiHandler):

    def get(self, *args, **kwargs):
        objects = [
            dict(url=url, response=response)
            for url, response
            in self.application.monitor.iter_urls()
        ]
        objects = sorted(
            objects, key=lambda x: x['response']['updated_at'], reverse=True
        )
        self.response({'objects': objects}, 200)


class UrlDetailsHandler(BaseApiHandler):

    def get(self, *args, **kwargs):
        url = self.get_argument('url', None)

        try:
            info = self.application.monitor.get_info(url=url)
            self.response({'response': info}, 200)
        except KeyError:
            error = u"Url: {} is not monitored".format(url)
            self.response({'error': error}, 400)