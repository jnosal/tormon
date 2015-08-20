import json
import datetime


FILE_READER = 'file'

MEMORY_WRITER = 'memory'
REDIS_WRITER = 'redis'

ALLOWED_READERS = [
    FILE_READER
]

ALLOWED_WRITERS = [
    MEMORY_WRITER
]


def handler_(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return str(obj)


def json_dumps(data):
    return json.dumps(data, default=handler_)


def json_loads(data):
    return json.loads(data)