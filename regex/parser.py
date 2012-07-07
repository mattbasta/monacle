from decider.cleaner import clean, PUNCTUATION


class PlaceholderToken(object):
    """A placeholder for a component of the user's query."""

    def __init__(self, name):
        self.name = name
        self.tokens = []


class Expression(object):
    """A representation of a query used for pattern matching."""

    def __init__(self, pattern, method=None, raw=None):
        self.pattern = pattern
        self.method = method
        self.raw = raw

    def matches(self, tokens, pattern_offset=0, prepend=None):
        if prepend is None:
            prepend = ()

        if pattern_offset:
            print "New offset:", pattern_offset
            print "New tokens:", tokens
            print "New pattern tokens:", prepend + tuple(self.pattern[pattern_offset:])
        enumer_tokens = enumerate(tokens)
        placeholders = {}
        token_index = 0

        toks_to_iterate = prepend + tuple(self.pattern[pattern_offset:])
        if not toks_to_iterate:
            return None

        for pattern_index, pattern_token in enumerate(toks_to_iterate):
            if isinstance(pattern_token, (list, tuple)):
                print "Hit subtoken block:", pattern_token
                for subtoken in pattern_token:
                    print "Testing subtoken", subtoken
                    matches = self.matches(
                            tokens[token_index + 1:],
                            pattern_offset=pattern_offset + pattern_index -
                                               len(prepend) + 1,
                            prepend=subtoken)
                    if matches is not None:
                        placeholders.update(matches)
                        return placeholders
                return None

            if isinstance(pattern_token, PlaceholderToken):
                placeholders[pattern_token.name] = []
                print "Found placeholder, matching deeper..."
                # Start churning user tokens until we can start forward
                # matching.
                for i, user_token in enumer_tokens:
                    matches = self.matches(
                        tokens[i:],
                        pattern_offset=pattern_offset + pattern_index -
                                       len(prepend) + 1)
                    # If the next chunk matches, don't re-traverse, just
                    # return.
                    if matches is not None:
                        placeholders.update(matches)
                        return placeholders

                    # While we haven't matched the next chunk, push to the
                    # placeholder output storage.
                    print "Bumping to placeholder %s:" % pattern_token.name, user_token
                    placeholders[pattern_token.name].append(user_token)

                return placeholders

            optional = pattern_token.startswith("[") and pattern_token.endswith("]")
            if optional:
                pattern_token = pattern_token[1:-1]
                temp_token_index, next_token = enumer_tokens.next()
                if next_token != pattern_token:
                    print "Skipped:", pattern_token
                    return self.matches(
                            tokens[temp_token_index:],
                            pattern_offset=pattern_offset + pattern_index -
                                           len(prepend) + 1)
                else:
                    print "Matched optional token:", pattern_token
                    token_index = temp_token_index
                    continue

            token_index, next_token = enumer_tokens.next()
            if pattern_token != next_token:
                # It's not a match, just drop out.
                print pattern_token, "did not match", next_token
                return None
            print "Found token", next_token

        return placeholders

    def run(self, tokens):
        data = self.matches(tokens)
        return self.method(data) if data is not None else None


def expr(pattern, method):
    clean_pattern = clean(pattern, expression=True)
    if clean_pattern[-1] in PUNCTUATION:
        clean_pattern = clean_pattern[:-1]
    parsed_pattern = []
    for token in clean_pattern:
        if not isinstance(token, str):
            parsed_pattern.append(token)
            continue
        if token.startswith("{{") and token.endswith("}}"):
            t = PlaceholderToken(token[2:-2])
            parsed_pattern.append(t)
            continue

        parsed_pattern.append(token)

    return Expression(parsed_pattern, method=method, raw=pattern)


def search_for(type, near="me"):
    """
    `type`:
        Can be 'place', 'thing'.
    `near`:
        Can be 'me' or a token name.
    """
    def wrap(tokens):
        pass
    return wrap


def action(type, service="google"):
    """
    `type`:
        Can be 'search', 'map'
    """
    def wrap(tokens):
        pass
    return wrap


def play(types):
    """
    `types`:
        List of choices from ["genre", "artist", "album", "track"]
    """

def weather(find_by=None, params=None):
    pass


QUERIES = [
    # Find places
    expr("where is the {{place}}", search_for("place")),
    expr("where is the nearest {{place}}", search_for("place")),
    expr("where is the closest {{place}}", search_for("place")),
    expr("find the nearest {{place}}", search_for("place")),
    expr("find {{thing}} near {{place}}", search_for("thing", near="place")),
    expr("find {{thing}} in {{place}}", search_for("thing", near="place")),

    # Directions
    expr("where is {{place}}", action("map")),
    expr("directions to {{place}}", action("map")),
    expr("get me directions to {{place}}", action("map")),
    expr("give me directions to {{place}}", action("map")),
    expr("take me to {{place}}", action("map")),
    expr("how do i get to {{place}}", action("map")),

    # Searching
    expr("look up {{query}} on youtube", action("search", service="youtube")),
    expr("look up {{query}}", action("search")),
    expr("search the web for {{query}}", action("search")),
    expr("search {{service}} for {{query}}", action("search", service=None)),
    expr("help me find a {{query}}", action("search", service="amazon")),
    expr("find [me] a {{query}}", action("search", service="amazon")),
    expr("what's going on with {{query}}", action("search", service="twitter")),

    # Music
    expr("play some {{music}}", play(["genre", "artist"])),
    expr("play {{music}}", play(["track", "artist", "album"])),
    expr("put on some {{music}}", play(["genre", "artist"])),
    expr("put on {{music}}", play(["artist", "track"])),
    expr("listen to {{music}}", play(["track", "artist"])),

    #Weather
    expr("what's (the weather|it) going to be [like] [outside] {{date}}", weather()),
    expr("what will (the weather|it) be [like [outside]] {{date}}", weather()),
    expr("will (the weather|it) be {{condition}} [outside]", weather(find_by="condition")),
    expr("will (the weather|it) be {{condition}} [outside] {{date}}", weather(find_by="condition", params=["date"])),
    expr("what's the temperature [outside]", weather(find_by="temperature")),
    expr("what's the temperature [outside] [going to be] {{date}}", weather(find_by="temperature", params=["date"])),
    expr("what will the temperature be [outside]", weather(find_by="temperature")),
    expr("what will the temperature be [outside] {{date}}", weather(find_by="temperature", params=["date"])),
]


def match_raw(query):
    return match(clean(query))

def match(tokens):
    for query in QUERIES:
        print "Attempting match against:", query.raw
        print query.pattern
        match = query.matches(tokens)
        if match is not None:
            return match
