from base import Response


class PlaceResponse(Response):
    def __init__(self, name, address=None, locality=None, region=None,
                 country=None):
        self.metadata = {}

        self.name = name
        self.address = address
        self.locality = locality
        self.region = region
        self.country = country

    def render(self):
        return {"type": "place",
                "name": self.name,
                "address": self.address,
                "locality": self.locality,
                "region": self.region,
                "country": self.country,
                "metadata": self.metadata}

