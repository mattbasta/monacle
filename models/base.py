import json


class Response(object):
    def render(self):
        return {"type": "noop"}

    def __str__(self):
        return json.dumps(self.render())

    def __unicode__(self):
        return unicode(self.__str__())


class MultiResponse(Response):
    def __init__(self):
        self.responses = []

    def push(self, response):
        self.responses.append(response)

    def render(self):
        return {"type": "multi",
                "responses": [r.render() if isinstance(r, Response) else r for
                              r in self.responses]}
