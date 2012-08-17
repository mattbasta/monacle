ENDPOINTS = {}


def endpoint(name):
    def wrap(func):
        ENDPOINTS[name] = func
        return func
    return wrap
