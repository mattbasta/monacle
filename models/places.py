from base import Response


class PlaceResponse(Response):
    def __init__(self, ob):
        self.ob = ob

    def render(self):
        data = {"type": "place"}
        render = self.ob.render()
        data.update(render)

        if "address" in render:
            data["zoom"] = 13
        elif "locality" in render:
            data["zoom"] = 11
        elif "region" in render:
            data["zoom"] = 6
        else:
            # Lat/Lon only
            data["zoom"] = 12

        return data
