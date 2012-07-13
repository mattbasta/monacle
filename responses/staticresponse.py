from response import BaseResponse


class StaticResponse(BaseResponse):

    def __init__(self, response):
        self.response = unicode(response)

    def as_text(self):
        return self.response
