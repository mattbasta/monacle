import constants

from factual import Factual
fs = constants.FACTUAL_SETTINGS
f = Factual(fs["key"], fs["secret"])
places = f.table("global")


class LatLon(object):
    def __init__(self, lat, lon):
        self.lat, self.lon = lat, lon

    def tup(self):
        return self.lat, self.long

    def render(self):
        return {"lat": self.lat, "lon": self.lon}


class Place(object):
    def __init__(self, locality=None, region=None, country=None):
        self.locality = locality
        self.region = region
        self.country = country

    def render(self):
        return {"locality": self.locality,
                "region": self.region,
                "country": self.country}


class Venue(object):
    def __init__(self, name, address=None, place=None, location=None):
        self.metadata = {}

        self.name = name
        self.address = address
        self.place = place
        self.location = location

    def render(self):
        out = {"type": "place",
               "name": self.name,
               "address": self.address,
               "metadata": self.metadata}
        if self.place:
            out.update(self.place.render())
        if self.location:
            out.update(self.location.render())
        return out


def search(query, userinfo, near=None, limit=1):
    pass

