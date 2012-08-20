import constants
import math

from factual import Factual
fs = constants.FACTUAL_SETTINGS
f = Factual(fs["key"], fs["secret"])
places = f.table("global")
geographies = f.table("world-geographies")


class LatLon(object):
    def __init__(self, lat, lon):
        self.lat, self.lon = map(float, (lat, lon))
        print "Lat Lon:", lat, lon

    def tup(self):
        return self.lat, self.lon

    def render(self):
        return {"lat": self.lat, "lon": self.lon}

    def coords(self):
        return self


class Place(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.center = kwargs.get("center", None)
        if self.center:
            assert isinstance(self.center, LatLon)
        self.locality = kwargs.get("locality", None)
        self.region = kwargs.get("region", None)
        self.country = kwargs.get("country", None)

    def render(self):
        out = {"name": self.name,
               "locality": self.locality,
               "region": self.region,
               "country": self.country}
        if self.center:
            out.update({"coords": self.center.render()})
        return out

    def coords(self):
        # This is really hacky, but it prevents failures and it doesn't give
        # weird results because this should only be used for sorting.
        return self.center or LatLon(0, 0)


class Venue(object):
    def __init__(self, name, address=None, place=None, location=None,
                 metadata=None):
        self.name = name
        self.address = address
        self.place = place
        self.location = location
        self.metadata = metadata

    def render(self):
        out = {"type": "place",
               "name": self.name,
               "address": self.address,
               "metadata": self.metadata}
        if self.place:
            out.update({"place": self.place.render()})
        if self.location:
            out.update({"coords": self.location.render()})
        return out

    def coords(self):
        return self.location or LatLon(0, 0)


nauticalMilePerLat = 60.00721
nauticalMilePerLongitude = 60.10793
rad = math.pi / 180.0
milesPerNauticalMile = 1.15078
def _dist(loc1, loc2):
    """
    Caclulate distance between two lat lons in NM
    """
    lat1, lon1 = loc1.tup()
    lat2, lon2 = loc2.tup()

    yDistance = (lat2 - lat1) * nauticalMilePerLat
    xDistance = (math.cos(lat1 * rad) + math.cos(lat2 * rad)) * \
                    (lon2 - lon1) * (nauticalMilePerLongitude / 2)
    distance = math.sqrt(yDistance**2 + xDistance**2)
    return distance * milesPerNauticalMile


def get_location(query, request, near="here", full_object=False):
    if isinstance(query, LatLon):
        if full_object:
            raise "Cannot return full object for structured data."
        return query
    elif isinstance(query, Venue):
        return query.location if not full_object else query
    elif isinstance(query, Place):
        return query.center if not full_object else query

    print "PLACES: Getting location for", query
    if query in ("here", "me", "where i am", "where i'm at", ):
        return LatLon(request.prop("latitude"),
                      request.prop("longitude"))

    # Search for a place first.
    place = get_place(query, request, near=near, secondary=True)
    if place:
        return place.center if not full_object else place

    # If it's not a place, search for a venue.
    venue = get_venue(query, request, near=near)
    if venue:
        return venue.location if not full_object else venue

    return None


PLACE_LIMIT_MIN = 10
SEC_PLACE_THRESH = 100  # Miles
def get_place(query, request, near="here", limit=1, secondary=False):
    """
    Return a place object corresponding to the given query.

    `near`:
        A place, venue, or LatLon object that describes where the place should
        be located near.
    `limit`:
        The maximum number of results to return.
    `secondary`:
        If this is not the object that is being returned to the user (i.e.: it
        is being used for an auxiliary task like a venue's `near` parameter),
        this should be set to True.
    """
    print "PLACES: Getting place for", query
    near = get_location(near, request)

    query = query.strip()

    q = geographies.search(query).filters({"name": {"$search": query}})
    q = q.limit(PLACE_LIMIT_MIN if limit <= PLACE_LIMIT_MIN else limit)

    placetypes = ["locality", "postcode", "colloquial"]
    if not secondary:
        placetypes += ["state", "county", "neighborhood", "timezone"]

    q = q.filters({"placetype": {"$in": placetypes}})
    # if near:
    #     q = q.geo({"$point": list(near.tup())})
    #     q = q.sort("$distance:asc")

    q = q.select("name,country,latitude,longitude,placetype")
    print "DEBUG:", q.path, q.params
    results = q.data()
    print "PLACES: %s > %s" % (query, results)

    if not results:
        return None

    def process(result):
        return Place(name=result["name"],
                     country=result["country"],
                     center=LatLon(result["latitude"], result["longitude"]))

    #return process(results[0]) if limit == 1 else map(process, results)

    # We have to do this until Factual starts letting us properly geo-sort.
    results = map(process, results)
    exact_results = filter(lambda x: x.name.lower() == query.lower(),
                           results)
    if exact_results:
        results = exact_results
    if near:
        near_loc = near.coords()
        _dd = lambda x: _dist(near_loc, x.coords())
        results = sorted(results, cmp=lambda x, y: cmp(_dd(x), _dd(y)))
        if secondary:
            results = filter(lambda r: _dd(r) <= SEC_PLACE_THRESH, results)

    if not results:
        return None

    return results[0] if limit == 1 else results


def get_venue(query, request, near="here", limit=1):
    print "PLACES: Getting venue for", query
    near = get_location(near, request)
    q = places.search(query).limit(limit)
    if near:
        print "Near", near
        q = q.geo({"$circle": {"$center": near.tup(),
                               "$meters": 50000}})
        q = q.sort("$distance:asc")

    print "DEBUG:", q.path, q.params
    results = q.data()
    print "PLACES: %s > %s" % (query, results)
    if not results:
        return None

    def process(result):
        place = Place(locality=result["locality"],
                      region=result["region"],
                      country=result["country"])
        return Venue(name=result["name"],
                     address=result["address"],
                     place=place,
                     metadata=result,
                     location=LatLon(result["latitude"], result["longitude"]))

    return process(results[0]) if limit == 1 else map(process, results)
    