import datetime
import json
import time

import pytz
import requests

from constants import GEONAMES_USERNAME
from helpers import detokenize
from models import StaticResponse
from services.places import get_location, get_place


def get_timezone_at_place(location):
    url = ("http://api.geonames.org/timezoneJSON?lat=%d&lng=%d&radius=200"
           "&username=%s" % (location.tup() + (GEONAMES_USERNAME, )))
    print "GEONAMES:", url
    return json.loads(requests.get(url).text)["timezoneId"]


def get_time_in_zone(timezone):
    timezone = pytz.timezone(timezone)
    t = datetime.datetime.now(timezone)
    return t.strftime("%I<b>:</b>%M %p")


def time_():
    @detokenize
    def wrap(data, request):
        if "place" not in data or data["place"] == "here":
            timezone = get_timezone_at_place(get_location("here", request))
            return StaticResponse('The time is currently <time>%s</time>' %
                                      get_time_in_zone(timezone))
        else:
            place = get_place(data["place"], request)
            if place is None:
                return StaticResponse("Sorry, I don't know where that is. :(")
            timezone = get_timezone_at_place(place.coords())
            return StaticResponse("The time in <em>%s</em> is <time>%s</time>" %
                                      (place.name, get_time_in_zone(timezone)))
    return wrap
