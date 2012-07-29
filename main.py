import redis
import tornado.ioloop
import tornado.template as template
import tornado.web

import constants
from controllers.initial import InitialHandler
from controllers.questions import QuestionHandler
import sessions


loader = template.Loader("templates/")
settings = {"project_name": constants.PROJECT_NAME,
            "my_name": constants.AI_NAME}


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("home.html").generate(**settings))


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.redis = redis.StrictRedis(**constants.REDIS_SETTINGS)
        self.session_store = sessions.RedisSessionStore(self.redis)


application = Application([
    (r"/", MainHandler),
    (r"/questions/initial", InitialHandler),
    (r"/questions/[a-zA-Z0-9]+", QuestionHandler),
])

if __name__ == "__main__":
    application.listen(constants.PORT)
    tornado.ioloop.IOLoop.instance().start()

