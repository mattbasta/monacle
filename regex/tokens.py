import types


class Token(object):
    """
    Class which all other token types derive from.
    """
    def __init__(self, raw):
        self.raw = None
        if raw is None:
            return

        if not isinstance(raw, types.StringTypes):
            raw = "".join(raw)
        raw = raw.lower().strip()
        self.raw = raw

    def ends(self, c):
        return True

    def post_end(self, c):
        pass

    def __str__(self):
        return '<Token value="%s" />' % self.raw

    def __repr__(self):
        return self.__str__()


class TokenContainer(Token):
    """A helper to manage tokens that can contain other tokens."""
    def __init__(self, *args, **kwargs):
        self.contents = []
        super(TokenContainer, self).__init__(*args, **kwargs)

    def push_token(self, token):
        self.contents.append(token)

    def alerts(self, char):
        pass


class OptionalToken(TokenContainer):
    """
    A token represented by `[foo]`. The contents of the token are optional and
    may be skipped if not matched.
    """
    def ends(self, c):
        return c == "]"

    def __str__(self):
        return '<OptionalToken>%s</OptionalToken>' % \
                "".join(map(str, self.contents))


class MultiToken(TokenContainer):
    """
    A token represented by `(foo|bar|zap)`. Any one of the subtokens may be
    matched, but not more than one or none.
    """
    def __init__(self, *args, **kwargs):
        self.branches = []
        super(MultiToken, self).__init__(*args, **kwargs)

    def alerts(self, c):
        return c == "|"

    def post_alert(self, c):
        if c == "|":
            self.branches.append(self.contents)
            self.contents = []
            return True

    def ends(self, c):
        return c == ")"

    def post_end(self, c):
        if c == ")":
            self.branches.append(self.contents)
            self.contents = None
            return True

    def __str__(self):
        return '<MultiToken><Branch>%s</Branch></MultiToken>' % \
                "</Branch><Branch>".join(map(str, self.branches))


class PlaceholderToken(TokenContainer):
    """A placeholder for a component of the user's query."""
    def ends(self, c):
        return False

    def __str__(self):
        return '<Placeholder />'

class SinglePlaceholderToken(PlaceholderToken):
    """A placeholder token for a single token rather than a collection."""
    def __str__(self):
        return '<SinglePlaceholder />'
