from services.places import get_location, get_place, get_venue


def detokenize(func):
    """
    By default, parameters are passed to endpoints in the form:
    {"placeholder": [<token>, <token>, ...]}

    This decorator typecasts the list of tokens to strings and concatenates
    them with spaces as delimiters:
    {"placeholder": "token1 token2 token3 ..."}
    """

    def wrap_detok(data, request):
        data = dict((k, " ".join(map(str, v))) for k, v in data.items())
        return func(data, request)
    return wrap_detok


def location(parameter):
    """
    Converts a detokenized data parameter to the result of a get_location
    search for the provided query.
    """
    def decorator(func):
        def wrap(data, request):
            data[parameter] = get_location(data.get(parameter), request)
            return func(data, request)
        return wrap
    return decorator


def place(parameter, near_parameter=None, limit=1):
    """
    Converts a detokenized data parameter to a field which provides a place
    object. If `near_parameter` is provided, the place will be sorted by the
    closest result to the place object provided at the specified parameter.
    """
    def decorator(func):
        def wrap(data, request):
            near = "here"
            if near_parameter:
                near = data.get(near_parameter, "here")

            data[parameter] = get_place(data.get(parameter), request,
                                        near=near, limit=limit)
            return func(data, request)
        return wrap
    return decorator


def venue(parameter, near_parameter=None, limit=1):
    """
    Converts a detokenized data parameter to a field which provides a venue
    object. If `near_parameter` is provided, the venue will be sorted by the
    closest result to the place object provided at the specified parameter.
    """
    def decorator(func):
        def wrap(data, request):
            near = "here"
            if near_parameter:
                near = data.get(near_parameter, "here")

            data[parameter] = get_venue(data.get(parameter), request,
                                        near=near, limit=limit)
            return func(data, request)
        return wrap
    return decorator
