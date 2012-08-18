import datetime
import time

import pytz

from models import StaticResponse


def time_():
    def wrap(data, userinfo=None):
        if "place" not in data or data["place"] == "here":
            return StaticResponse("The time is currently %s" %
                                      time.strftime("%I:%M %p"))
        else:
            place = " ".join(
                map(lambda x: x[0].upper() + x[1:].lower(),
                    map(str, data["place"])))
            timezone = pytz.timezone("America/%s" % place.replace(" ", "_"))
            t = datetime.datetime.now(timezone)
            return StaticResponse("The time in %s is %s" %
                                      (place, t.strftime("%I:%M %p")))
    return wrap
