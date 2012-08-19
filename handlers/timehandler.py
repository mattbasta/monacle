import datetime
import time

import pytz

from helpers import detokenize
from models import StaticResponse


def time_():
    @detokenize
    def wrap(data, request):
        if "place" not in data or data["place"] == "here":
            return StaticResponse('The time is currently <time>%s</time>' %
                                      time.strftime("%I<b>:</b>%M %p"))
        else:
            place = " ".join(map(lambda x: x[0].upper() + x[1:].lower(),
                                 data["place"].split(" ")))
            timezone = pytz.timezone("America/%s" % place.replace(" ", "_"))
            t = datetime.datetime.now(timezone)
            return StaticResponse("The time in <em>%s</em> is <time>%s</time>" %
                                      (place, t.strftime("%I<b>:</b>%M %p")))
    return wrap
