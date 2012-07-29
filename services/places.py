import constants

from factual import Factual
fs = constants.FACTUAL_SETTINGS
f = Factual(fs["key"], fs["secret"])
places = f.table("global")


class LatLon(object):
    def __init__(self, lat, lon):
        self.lat, self.lon = lat, lon


def search(query, userinfo, near=None, limit=1):
    pass

