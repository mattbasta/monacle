from helpers import detokenize, location, venue
from models import PlaceResponse, StaticResponse
from services.places import get_location, get_place


@detokenize
def find_location(data, request):
    query = data.get("place", "here")
    loc = get_location(query, request, full_object=True)
    if loc:
        resp = PlaceResponse(loc).render()
        if query == "here":
            resp["name"] = "Your location"
        return resp

    # Try again, but this time, search the full set of places (the above only
    # searches primary places.
    loc = get_place(query, request, secondary=False)
    if loc:
        return PlaceResponse(loc)

    return StaticResponse("Sorry, we couldn't find that place.")


@detokenize
@venue("place", near_parameter="near")
@location("near")
def find_venue(data, request):
    loc = data.get("place")
    if not loc:
        return StaticResponse("Sorry, we couldn't find that place.")
    return PlaceResponse(loc)
