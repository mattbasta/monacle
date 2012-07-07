import tornado.web

import sessions


class BaseHandler(tornado.web.RequestHandler):
    def current_user(self):
        return (self.session["user"] if
                self.session and "user" in self.session else
                None)

    @property
    def session(self):
        session_id = self.get_secure_cookie("sid")
        return sessions.Session(self.application.session_store, session_id)
