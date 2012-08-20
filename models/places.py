from base import Response


class PlaceResponse(Response):
    def __init__(self, ob):
        self.ob = ob

    def render(self):
        data = {"type": "place"}
        data.update(self.ob.render())

        if "address" in data:
            data["zoom"] = 15
        elif "locality" in data:
            data["zoom"] = 12
        elif "region" in data:
            data["zoom"] = 6
        else:
            # Lat/Lon only
            data["zoom"] = 12

        if "name" not in data:
            data["name"] = "Coordinates"
        if "address" not in data:
            data["address"] = None
        if "locality" not in data:
            data["locality"] = None
        if "region" not in data:
            data["region"] = None

        # Filter the metadata
        if "metadata" in data:
            for key in data["metadata"].keys():
                if key in data or ("place" in data and key in data["place"]):
                    del data["metadata"][key]

        return data
