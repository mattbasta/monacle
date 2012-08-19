from . import endpoint, ENDPOINTS
from base import BaseHandler
from initial import BASE_QUESTION
import models
import questiontext
from regex.query_parser import get_response


class QuestionHandler(BaseHandler):
    """
    Respond to an answer with an appropriate response.
    """
    def get(self, endpoint):
        if endpoint not in ENDPOINTS:
            self.send_error(400)
            return

        self.write(ENDPOINTS[endpoint](self))


@endpoint("question")
def question_endpoint(request):
    query = request.prop("response")
    resp = get_response(query, request)
    responses = models.MultiResponse()

    if not resp:
        responses.push(models.StaticResponse(questiontext.SORRY))
    else:
        try:
            responses.push(resp)
        except Exception as e:
            print e
            responses.push(models.StaticResponse(questiontext.SORRY))
    responses.push(models.TextQuestion(questiontext.ANYTHING_ELSE, endpoint="question"))
    return responses
