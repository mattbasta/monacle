ENDPOINTS = {}

def register_endpoint(key):
    def decorator(f):
        ENDPOINTS[key] = f
        return f
    return decorator


def get_endpoint(key):
    return ENDPOINTS[key]

