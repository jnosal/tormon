import tornado.testing


class BaseTestCase(tornado.testing.AsyncTestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
