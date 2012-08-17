from base import Response


class Question(Response):
    def __init__(self, question, endpoint=None):
        self.question = question
        self.endpoint = endpoint

    def render(self):
        resp = {"type": "question",
                "text": self.question,
                "endpoint": self.endpoint}
        resp.update(self._render())
        return resp


class TextQuestion(Question):
    def _render(self):
        return {"type": "textquestion"}


class ChoicesQuestion(Question):
    def __init__(self, choices, *args, **kwargs):
        super(ChoicesQuestion, self).__init__(*args, **kwargs)
        self.choices = choices

    def _render(self):
        return {"type": "choices", "choices": self.choices}
