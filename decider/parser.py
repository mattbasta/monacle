from collections import deque
import re

import nltk


word_tags = {}
word_expansions = {}

stop_chars = "0123456789`~!@#$%^&*()-_=+ ;:\"\\,./<>?[]{}|"
ignored_tags = ("^", "FW-", "-HL", "-TL", "-NC", "NIL", "UH")
def setup():
    supported_corpora = [nltk.corpus.treebank, nltk.corpus.brown]
    pos_boundaries = re.compile("[\-\+]")

    # Load the word tags for the supported corpora.
    for corpus in supported_corpora:
        for word, pos in corpus.tagged_words():
            # Filter out any misspelled words
            if (pos.startswith(ignored_tags) or pos.endswith(ignored_tags) or
                any(it in pos for it in ignored_tags)):
                continue
            # Filter out words with numbers or symbols
            if len(word) > 1 and any(c in word for c in stop_chars):
                continue

            # Force "to" to be "TO"
            if word == "to":
                pos = "TO"

            # Create the tag set if it doesn't exist
            if pos not in word_tags:
                word_tags[pos] = set()
            # Put the word in the tag
            word_tags[pos].add(word.lower())

            if pos_boundaries.search(pos):
                pos_split = pos_boundaries.split(pos)
                if (word not in word_expansions or
                    len(word_expansions[word]) < len(pos_split)):
                    word_expansions[word] = pos_split

if __name__ == "decider.parser":
    setup()


def _parts_of_speech(tokens):
    def tag_token(token):
        token = token.lower()
        if token in word_expansions:
            return [(token, set(e_el)) for e_el in word_expansions[token]]
        return token, set(filter(lambda t: token in word_tags[t],
                                 word_tags.keys()))

    for tag in map(tag_token, tokens):
        if isinstance(tag, tuple):
            yield tag
        else:
            for t in tag:
                yield t


class ClusteredTokens(object):
    """
    A series of tokens that have been grouped together by a parser rule. This
    cluster is used to build the parse tree(s) for a command or query.
    """

    def __init__(self, tokens, type):
        self.tokens = tokens
        self.type = type

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<ParseNode type="%s">%s</ParseNode>' % (
                self.type, "\n".join(map(str, self.tokens)))


class ComparableRule(object):
    """
    An object that can be compared to a tagged token to determine whether it is
    an appropriate match for the current rule sequence.
    """
    def __init__(self, token_types):
        self.tt = (token_types if isinstance(token_types, set) else
                   set([token_types]))

    def matches(self, token):
        if isinstance(token, ClusteredTokens):
            return token.type in self.tt

        try:
            if not token[1] and not self.tt:
                return True
            return set(token[1]).intersection(self.tt) or False
        except:
            import pdb; pdb.set_trace()


def _subrule(*tokens):
    return map(ComparableRule, tokens)


parser_rules = {
    "COMMAND": [_subrule("QUESTION")],
    "QUESTION": [_subrule("WP", "QUESTION_BODY", "."),  # What ...?
                 _subrule("WRB", "QUESTION_BODY", ".")],  # Where ...?
    "QUESTION_BODY": [_subrule("OBJECT", "VBZ", "OBJECT"),  # What day is ...?
                      # What is the ...?
                      _subrule("VBZ", "OBJECT"),
                      _subrule("VBZ", "OBJECT", "QUALIFIER"),
                      _subrule("MD", "OBJECT", "QUALIFIER")],
    "NOUN": [_subrule("NN"),
             _subrule(set()),],
    "OBJECT": [_subrule("DT", "NOUN"),  # the pizza
               _subrule("NOUN", "NOUN"),  # pizza guy
               _subrule("OBJECT", "NOUN"), ],  # the pizza guy
    "QUALIFIER": [_subrule("VBZ", "DESCRIPTOR"),
                  _subrule("VB", "DESCRIPTOR")],
    }


def parse(question):
    words = nltk.word_tokenize(question)
    if len(words) > 20:
        raise QueryTooLongException()

    tags = _parts_of_speech(words)
    return tags


class CommandParser(object):
    """
    This is the parser that will parse the command and return the appropriate
    parse tree based on the grammer defined above.

    This parser assumes that it will receive at least one token in the token
    stream.
    """

    def __init__(self, tokens):
        self.t = deque(tokens)

        self.stack = []
        self.stack.append(self.t.popleft())

    def _matches(self, subrule):
        subset = self.stack[-len(subrule):]
        return all(r.matches(t) for r, t in zip(subrule, subset))

    def _reduce(self):
        for rule in parser_rules:
            for subrule in parser_rules[rule]:
                sr_len = len(subrule)
                if sr_len > len(self.stack): continue

                if self._matches(subrule):
                    cluster = ClusteredTokens(self.stack[-sr_len:], rule)
                    self.stack = self.stack[:-sr_len]
                    self.stack.append(cluster)
                    return True

    def run(self):
        while 1:
            # Collapse any rules that can be collapsed.
            while 1:
                if not self._reduce():
                    break

            if not self.t:
                return self.stack

            # Push back another token onto the stack.
            self.stack.append(self.t.popleft())

        return self.stack


def _parser(tokens):
    parser = CommandParser(tokens)
    return parser.run()

