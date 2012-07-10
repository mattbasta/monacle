import types

from optimizer import compact
from tokens import *


class QueryTooLongException(Exception):
    """
    This exception is thrown when a query is too long to parse in a reasonable
    amount of time. When this exception is encountered, the client should be
    presented with a message asking them to rephrase their question for
    brevity.
    """
    MAX_QUERY_LENGTH = 20


PUNCTUATION = ":;,.?!()"
ABBREV_PUNCTUATION = ":;,.?!"


class ExpressionParser(object):

    def __init__(self, expression, expressive=True):
        print "Parsing %s" % expression
        self.expression = expression
        self.expressive = expressive
        self.token_stack = []

        self.char_gen = None
        self.char_gen = self.chars()
        self.buffer = []

        self.tokens = []

    def chars(self):
        if self.char_gen is not None:
            return self.char_gen
        return iter(self.expression)

    def push_buffer(self, char):
        self.buffer.append(char)

    def pop_buffer_token(self):
        if not self.buffer:
            return
        self.push_token(self.buffer)
        self.buffer = []

    def push_token(self, token):
        if isinstance(token, list):
            token = "".join(token)
        if isinstance(token, types.StringTypes):
            if token.startswith("{{") and token.endswith("}}"):
                token = PlaceholderToken(token[2:-2])
            elif token.startswith("{") and token.endswith("}"):
                token = SinglePlaceholderToken(token[1:-1])
            else:
                token = Token(token)
        if self.token_stack:
            return self.token_stack[-1].push_token(token)
        self.tokens.append(token)

    def parse(self):
        chars = self.chars()

        token_triggers = {"(": MultiToken, "[": OptionalToken}

        for c in chars:
            if self.expressive:
                if self.token_stack:
                    token_action = self.token_stack[-1].ends(c)

                    # None and True discard the character.
                    if token_action:
                        self.pop_buffer_token()
                        self.token_stack[-1].post_end(c)
                        self.push_token(self.token_stack.pop())
                        continue

                    if self.token_stack[-1].alerts(c):
                        self.pop_buffer_token()
                        self.token_stack[-1].post_alert(c)
                        continue

                if c in token_triggers:
                    self.pop_buffer_token()
                    m = token_triggers[c](None)
                    self.token_stack.append(m)
                    continue

            if c in PUNCTUATION:
                self.pop_buffer_token()
                self.tokens.append(Token(c))
                continue
            elif c == " ":
                self.pop_buffer_token()
                continue

            self.push_buffer(c)

        self.pop_buffer_token()

        print self.tokens


def tokenize_expression(expression, expressive=True):
    p = ExpressionParser(expression, expressive)
    p.parse()
    return p.tokens


def clean(string, expression=False):
    """Returns a list of tokens for the given query or expression."""
    tokens = tokenize_expression(string, expressive=expression)
    tokens = list(compact(tokens))

    if len(tokens) > QueryTooLongException.MAX_QUERY_LENGTH:
        raise QueryTooLongException()
    return tokens

