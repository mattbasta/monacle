import json

from controllers.base import BaseHandler


class Model(object):
    def __init__(self, endpoint, via):
        self.via = via
        self.endpoint = endpoint
        self.type = "Query"
        self.properties = {}

    def __str__(self):
        return json.dumps({"type": self.type,
                           "properties": self.properties})


class TextQuestion(Model):
    def __init__(self, question, endpoint, via):
        super(TextQuestion, self).__init__(endpoint, via)
        self.properties = {"question": question}
