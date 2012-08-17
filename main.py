import os
import uuid

import redis
import tornado.ioloop
import tornado.template as template
import tornado.web

import constants
from controllers.initial import InitialHandler
from controllers.questions import QuestionHandler


loader = template.Loader("templates/")
settings = {"project_name": constants.PROJECT_NAME,
            "my_name": constants.AI_NAME}


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(loader.load("home.html").generate(**settings))

class UniqidHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(uuid.uuid4()))

class PostHandler(tornado.web.RequestHandler):
    def post(self):
        print "Posted:", self.get_argument("type")
        self.write("Thanks")


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        #self.redis = redis.StrictRedis(**constants.REDIS_SETTINGS)
        #self.session_store = sessions.RedisSessionStore(self.redis)
        #self.session_store = sessions.MemorySessionStore()


application = Application([
    (r"/", MainHandler),
    (r"/static/(.*)",
         tornado.web.StaticFileHandler,
         {"path": os.path.join(os.path.dirname(__file__),
                               "static")}),
    (r"/uniqid", UniqidHandler),
    (r"/postdata", PostHandler),
    (r"/questions", InitialHandler),
    (r"/questions/([a-zA-Z0-9\.]+)", QuestionHandler),
], cookie_secret=constants.COOKIE_SECRET)

if __name__ == "__main__":
    application.listen(constants.PORT)
    tornado.ioloop.IOLoop.instance().start()

