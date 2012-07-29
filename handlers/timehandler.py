import time

from models import StaticResponse


def time_():
    def wrap(place="here", userinfo=None):
        return StaticResponse("The time is currently %s" %
                                  time.strftime("%I:%M %p"))
    return wrap
