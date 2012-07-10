from tokens import *


CONTRACTIONS = {
    "can't": ["cannot"],
    "won't": ["will", "not"],
    "shan't": ["shall", "not"],
}

CONTRACTION_TYPES = {
    "'d": "would",
    "'s": "is",
    "'ve": "have",
    "'re": "are",
    "'ll": "will",
    "n't": "not",
}

def compact(tokens):
    for token in tokens:
        if isinstance(token, MultiToken):
            branches = []
            for branch in token.branches:
                branches.append(tuple(compact(branch)))
            token.branches = branches
            yield token
            continue
        elif isinstance(token, OptionalToken):
            token.contents = tuple(compact(token.contents))
            yield token
            continue

        if token in CONTRACTIONS:
            for t in CONTRACTIONS[token]:
                yield Token(t)
            continue

        broke = False
        for ctype in CONTRACTION_TYPES:
            if token.raw.endswith(ctype):
                yield Token(token.raw[:-len(ctype)])
                yield Token(CONTRACTION_TYPES[ctype])
                broke = True
                break
        if not broke:
            yield token

