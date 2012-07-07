from compactor import compact


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


def word_processor(words, punctuation=None):
    if punctuation is None:
        punctuation = PUNCTUATION
    for word in words:
        if all(p not in word for p in punctuation):
            yield word
            continue

        # Handle punctuation
        buffer = []
        for c in word:
            if c in PUNCTUATION:
                yield "".join(buffer)
                buffer = []
                yield c
            else:
                buffer.append(c)
        if buffer:
            yield "".join(buffer)


def tokenize(string):
    return word_processor(string.split(" "))


def tokenize_expression(expression):
    print "Tokenizing expression %s" % expression
    def words():
        buffer = []
        paren_levels = 0
        for char in expression:
            # TODO: Yield binary optionals as their own objects.
            if char == "(":
                paren_levels += 1
            elif char == ")":
                paren_levels -= 1

            # TODO: Handle unary optionals here.

            if char == " " and not paren_levels:
                yield "".join(buffer)
                buffer = []
                continue
            buffer.append(char)

        yield "".join(buffer)

    for word in word_processor(words(), ABBREV_PUNCTUATION):
        if word.startswith("(") and word.endswith(")"):
            # TODO: This should handle multiple-level optionals (the split
            # breaks the support).
            yield tuple([tokenize_expression(b) for b in word[1:-1].split("|")])
        else:
            yield word


def clean(string, expression=False):
    """Returns a list of tokens for the given query or expression."""
    tokenizer = tokenize_expression if expression else tokenize
    tokens = [w.lower().strip() if isinstance(w, str) else w for
              w in tokenizer(string)]
    tokens = list(compact(tokens))

    if len(tokens) > QueryTooLongException.MAX_QUERY_LENGTH:
        raise QueryTooLongException()
    return tokens

