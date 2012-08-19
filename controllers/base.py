import json

import tornado.web

from models.base import Response


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.luggage = {}

    def gid(self):
        return self.prop("gid")

    def has_prop(self, key):
        return self.get_argument(key, default=None) is not None

    def prop(self, key):
        return self.get_argument(key)

    def stow(self, key, value):
        self.luggage[key] = value

    def write(self, data):
        if issubclass(type(data), Response):
            data = data.render()
        if isinstance(data, dict) and self.luggage:
            data.update({"luggage": self.luggage})
        if isinstance(data, dict):
            print data
            data = json.dumps(data)
        elif not isinstance(data, (str, unicode)):
            data = unicode(data)
        super(BaseHandler, self).write(data)
