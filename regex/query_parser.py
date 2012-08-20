from handlers import time, find_location, find_venue
import helpers
from parser import clean, PUNCTUATION
from tokens import *


class Expression(object):
    """A representation of a query used for pattern matching."""

    def __init__(self, pattern, method=None, raw=None):
        self.pattern = tuple(pattern)
        self.method = method
        self.raw = raw

    def matches(self, tokens, pattern):
        if pattern is None:
            return None

        enumer_tokens = enumerate(tokens)
        placeholders = {}
        token_index = -1

        print "New tokens:", tokens
        print "New pattern tokens:", pattern

        for pattern_index, pattern_token in enumerate(pattern):
            if isinstance(pattern_token, MultiToken):
                print "Hit subtoken block:", repr(pattern_token)
                for subtoken in pattern_token.branches:
                    matches = self.matches(
                            tokens[token_index + 1:],
                            subtoken + pattern[pattern_index + 1:])
                    if matches is not None:
                        placeholders.update(matches)
                        return placeholders
                return None

            if isinstance(pattern_token, PlaceholderToken):
                placeholders[pattern_token.raw] = []
                print "Found placeholder, matching deeper..."

                # If we end the pattern with a placeholder, just return the
                # rest of the values as the placeholder
                if pattern_index + 1 == len(pattern):
                    for i, user_token in enumer_tokens:
                        placeholders[pattern_token.raw].append(user_token)
                    return placeholders

                # Start churning user tokens until we can start forward
                # matching.
                for i, user_token in enumer_tokens:
                    matches = self.matches(
                        tokens[i:], pattern[pattern_index + 1:])
                    # If the next chunk matches, don't re-traverse, just
                    # return.
                    if matches is not None:
                        placeholders.update(matches)
                        return placeholders

                    # While we haven't matched the next chunk, push to the
                    # placeholder output storage.
                    placeholders[pattern_token.raw].append(user_token)

                return None

            if isinstance(pattern_token, OptionalToken):
                print "Testing optional branch"
                matches = self.matches(
                        tokens[token_index + 1:],
                        pattern_token.contents + pattern[pattern_index + 1:])
                if matches is None:
                    print "Skipped:", repr(pattern_token)
                    return self.matches(
                            tokens[token_index + 1:],
                            pattern[pattern_index + 1:])
                else:
                    placeholders.update(matches)
                    return placeholders

            try:
                token_index, next_token = enumer_tokens.next()
            except StopIteration:
                return placeholders

            if isinstance(pattern_token, SinglePlaceholderToken):
                placeholders[pattern_token.raw] = [next_token]
                print "Found single placeholder:", next_token.raw
            elif pattern_token.raw != next_token.raw:
                # It's not a match, just drop out.
                print pattern_token.raw, "did not match", next_token.raw
                return None
            else:
                print "Found token:", next_token.raw

        return placeholders

    def run(self, tokens):
        return self.matches(tokens, self.pattern)


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
    def wrap(data, request):
        pass
    return wrap


def action(type, service="google"):
    """
    `type`:
        Can be 'search', 'map'
    """
    def wrap(data, request):
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
    expr("where [[in] the (world|hell|fuck)] am i", find_location),
    expr("(where (is|are|can i find) [there]|find) [(a|an)] {{place}} (near|by|in|to) {{near}}", find_venue),
    expr("find [(a|an|the)] {{place}} ((closest|nearest) to|by|in) {{near}}", find_venue),
    expr("(where (is|are|can i find)|find) [(a|an|the)] [(nearest|closest)] {{place}}", find_location),

    # Directions
    expr("find [(a way|directions) to] {{place}}", find_location),
    expr("(get|give me) directions (to|for) {{place}}", find_location),
    expr("(how do i get|take me) to {{place}}", find_location),

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
        print "~" * 72
        print "Attempting match against:", query.pattern
        match = query.run(tokens)
        if match is not None:
            return match, query


def get_response(query, userinfo):
    """Return the appropriate response for the query and user info."""

    m = match(clean(query))
    if not m:
        return None
    data, method = m
    return method.method(data, userinfo)
