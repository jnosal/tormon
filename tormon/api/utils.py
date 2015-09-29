import datetime
import json


def handler_(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return str(obj)


def json_dumps(data):
    return json.dumps(data, default=handler_)


def json_loads(data):
    return json.loads(data)