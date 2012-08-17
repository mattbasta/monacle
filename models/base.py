import json


class Response(object):
    def render(self):
        return {"type": "noop"}

    def __str__(self):
        return json.dumps(self.render())

    def __unicode__(self):
        return unicode(self.__str__())
