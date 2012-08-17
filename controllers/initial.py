from . import endpoint
from base import BaseHandler
import models
import questiontext as questions


BASE_QUESTION = models.TextQuestion(questions.HELLO, endpoint="question")


class InitialHandler(BaseHandler):
    """
    Figure out what the user needs and broadcast the initial query.
    """
    def get(self):
        if not self.has_prop("user_name"):
            self.write(models.TextQuestion(questions.WHAT_IS_YOUR_NAME,
                                           endpoint="user.name"))
        else:
            self.write(BASE_QUESTION)


@endpoint("user.name")
def user_name(request):
    name = request.prop("response")
    request.stow("user_name", name)
    return BASE_QUESTION
