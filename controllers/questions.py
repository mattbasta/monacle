from . import ENDPOINTS
from base import BaseHandler
import models
import questions


class QuestionHandler(BaseHandler):
    """
    Respond to an answer with an appropriate response.
    """
    def get(self, endpoint):
        if endpoint not in ENDPOINTS:
            self.send_error(400)
            return

        self.write(ENDPOINTS[endpoint](self))
