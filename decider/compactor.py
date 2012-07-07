
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
        if not isinstance(token, (str, unicode)):
            yield tuple(compact(token))
            continue

        if token in CONTRACTIONS:
            for t in CONTRACTIONS[token]:
                yield t
            continue

        broke = False
        for ctype in CONTRACTION_TYPES:
            if token.endswith(ctype):
                yield token[:-len(ctype)]
                yield CONTRACTION_TYPES[ctype]
                broke = True
                break
        if not broke:
            yield token

