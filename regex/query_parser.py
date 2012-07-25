from handlers import time
from parser import clean, PUNCTUATION
from tokens import *


class Expression(object):
    """A representation of a query used for pattern matching."""

    def __init__(self, pattern, method=None, raw=None):
        self.pattern = pattern
        self.method = method
        self.raw = raw

    def matches(self, tokens, pattern_offset=0, prepend=None):
        if prepend is None:
            prepend = ()

        enumer_tokens = enumerate(tokens)
        placeholders = {}
        token_index = -1

        toks_to_iterate = prepend + tuple(self.pattern[pattern_offset:])
        if not toks_to_iterate:
            return None

        if pattern_offset:
            print "New offset:", pattern_offset
            print "New tokens:", tokens
            print "New pattern tokens:", toks_to_iterate

        for pattern_index, pattern_token in enumerate(toks_to_iterate):
            if isinstance(pattern_token, MultiToken):
                print "Hit subtoken block:", pattern_token
                for subtoken in pattern_token.branches:
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
                placeholders[pattern_token.raw] = []
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
                    placeholders[pattern_token.raw].append(user_token)

                return placeholders

            if isinstance(pattern_token, OptionalToken):
                matches = self.matches(
                        tokens[token_index + 1:],
                        pattern_offset=pattern_offset + pattern_index -
                                       len(prepend) + 1,
                        prepend=pattern_token.contents)
                if matches is None:
                    print "Skipped:", pattern_token
                    return self.matches(
                            tokens[token_index + 1:],
                            pattern_offset=pattern_offset + pattern_index -
                                           len(prepend) + 1)
                else:
                    placeholders.update(matches)
                    return placeholders

            try:
                token_index, next_token = enumer_tokens.next()
            except StopIteration:
                return placeholders

            if isinstance(pattern_token, SinglePlaceholderToken):
                placeholders[pattern_token.raw] = [next_token]
                print "Found single placeholder", next_token.raw
            elif pattern_token.raw != next_token.raw:
                # It's not a match, just drop out.
                print pattern_token.raw, "did not match", next_token.raw
                return None
            else:
                print "Found token", next_token.raw

        return placeholders

    def run(self, tokens, userinfo=None):
        data = self.matches(tokens)
        return self.method(data, userinfo) if data is not None else None


def expr(pattern, method):
    clean_pattern = clean(pattern, expression=True)
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
    expr("(where is|find) [(a|an|the)] [(nearest|closest)] {{place}}", search_for("place")),
    expr("(where is|find) [(a|an|the)] {{thing}} (near|by) [the] {{place}}", search_for("thing", near="place")),

    # Directions
    expr("where is {{place}}", action("map")),
    expr("find [(a way|directions) to] {{place}}", action("map")),
    expr("(get|give me) directions (to|for) {{place}}", action("map")),
    expr("(how do i get|take me) to {{place}}", action("map")),

    # Searching
    expr("look up {{query}} [on {{service}}]", action("search")),
    expr("search [the (web|net)] [for] {{query}} [on {{service}}]", action("search")),
    expr("search {{service}} for {{query}}", action("search", service=None)),
    expr("help me find [(a|an)] {{query}}", action("search")),
    expr("find [me] a {{query}}", action("search", service="amazon")),
    expr("what's going on with {{query}}", action("search", service="twitter")),

    # Music
    expr("play some {{music}}", play(["genre", "artist"])),
    expr("play {{music}}", play(["track", "artist", "album"])),
    expr("put on some {{music}}", play(["genre", "artist"])),
    expr("put on {{music}}", play(["artist", "track"])),
    expr("listen to {{music}}", play(["track", "artist"])),

    # Weather
    expr("what is (the weather [{{date}}]|it) [going] to be [like] [outside] [{{date}}]", weather()),
    expr("what will (the weather [{{date}}]|it) be [like] [outside] [{{date}}]", weather()),
    expr("will (the weather [{{date}}]|it) be {{condition}} [outside]", weather(find_by="condition")),
    expr("will (the weather [{{date}}]|it) be {{condition}} [outside]", weather(find_by="condition")),
    expr("what is (the weather in {{place}}|it) [going] to be [like] [outside] [in {{place}}] [{{date}}]", weather()),
    expr("what will (the weather [{{date}}]|it) be [like] [outside] [{{date}}]", weather()),
    expr("will (the weather [{{date}}]|it) be {{condition}} [outside]", weather(find_by="condition")),
    expr("will (the weather [{{date}}]|it) be {{condition}} [outside]", weather(find_by="condition")),

    # Time
    expr("what time is it [in {{place}}]", time()),
    expr("what is the [current] time [in {{place}}]", time()),
]


def match(tokens):
    if isinstance(tokens[-1], Token) and tokens[-1].raw in PUNCTUATION:
        tokens = tokens[:-1]
    for query in QUERIES:
        print "Attempting match against:", query.pattern
        match = query.matches(tokens)
        if match is not None:
            return match, query


def get_response(query, userinfo):
    """Return the appropriate response for the query and user info."""

    data, method = match(clean(query))
    return method.run(data, userinfo)
