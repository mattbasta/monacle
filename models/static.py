from base import Response


class StaticResponse(Response):
    def __init__(self, response):
        self.response = response

    def render(self):
        return {"type": "static", "text": self.response}
