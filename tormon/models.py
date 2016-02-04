DEFAULT_STRATEGY = u'pass'


def resources_from_dicts(data):
    for el in data:
        instance = Resource(
            url=el[u'url'],
            strategy=el[u'strategy']
        )
        yield instance


class Resource(object):

    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.strategy = kwargs.get(u'strategy', DEFAULT_STRATEGY)

    def __str__(self):
        return u"{0}".format(self.url)

    def __unicode__(self):
        return u"{0}".format(self.url)

    def __repr__(self):
        return u"{0}".format(self.url)