import os

root = lambda *x: os.path.join(os.path.dirname(__file__), *x)

APP_ROOT = root()
STATIC_ROOT = root('static')
TEMPLATE_ROOT = root('templates')
