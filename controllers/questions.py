
from base import BaseHandler
import models
import questions


class QuestionHandler(BaseHandler):
    """
    Respond to an answer with an appropriate response.
    """
    def get(self):
        user = self.current_user()
        if user is None:
            return
        # TODO: IDK
