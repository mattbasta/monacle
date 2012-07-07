from base import BaseHandler
import models
import questions


class InitialHandler(BaseHandler):
    """
    Figure out what the user needs and broadcast the initial query.
    """
    def get(self):
        user = self.current_user()
        if user is None:
            self.write(models.TextQuestion(questions.WHAT_IS_YOUR_NAME,
                                           endpoint="user.name",
                                           via=self))
        else:
            self.write(models.TextQuestion(questions.HELLO,
                                           endpoint="question",
                                           via=self))

