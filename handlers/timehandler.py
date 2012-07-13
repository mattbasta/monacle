import time

from responses import StaticResponse


def time_():
    def wrap(place="here"):
        return StaticResponse("The time is currently %s" %
                                  time.strftime("%I:%M %p"))
    return wrap
