ENDPOINTS = {}


def endpoint(name):
    def decorator(func):
        ENDPOINTS[name] = func
        return func
    return decorator
