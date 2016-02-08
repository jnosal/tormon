def resources_from_dicts(data):
    for el in data:
        instance = Resource(
            url=el[u'url']
        )
        yield instance


class Resource(object):

    def __init__(self, url, *args, **kwargs):
        self.url = url

    def __str__(self):
        return u"{0}".format(self.url)

    def __unicode__(self):
        return u"{0}".format(self.url)

    def __repr__(self):
        return u"{0}".format(self.url)


class Response(object):

    def __init__(self, *args, **kwargs):
        self.code = kwargs.get(u'code')
        self.headers = kwargs.get(u'headers')
        self.request_time = kwargs.get(u'request_time')
        self.updated_at = kwargs.get(u'updated_at')

    def as_dict(self):
        keys = [
            u'code', u'headers', u'request_time', u'updated_at'
        ]
        return dict(
            (key, getattr(self, key, None)) for key in keys
        )


class RequestError(object):

    def __init__(self, *args, **kwargs):
        self.code = kwargs.get(u'code')
        self.headers = kwargs.get(u'headers')
        self.request_time = kwargs.get(u'request_time')
        self.updated_at = kwargs.get(u'updated_at')
        self.message = kwargs.get(u'message')

    def as_dict(self):
        keys = [
            u'code', u'headers', u'request_time', u'updated_at', u'message'
        ]
        return dict(
            (key, getattr(self, key, None)) for key in keys
        )

