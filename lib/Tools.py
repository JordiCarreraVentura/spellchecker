import csv
import nltk
import re

from collections import (
    Counter,
    defaultdict as deft
)

from nltk import (
    ngrams,
    sent_tokenize as splitter,
    wordpunct_tokenize as tokenizer
)

from nltk.corpus import stopwords

from nltk.probability import FreqDist


NUM = re.compile('[0-9]')
NON_ALPHA = re.compile('[^a-z]', re.IGNORECASE)

STOPWORDS = deft(bool)
for w in stopwords.words('english'):
    STOPWORDS[w] = True


def decode(string):
    try:
        return string.decode('utf-8')
    except Exception:
        return string


def encode(string):
    try:
        return string.encode('utf-8')
    except Exception:
        return string


def remove_nonwords(items):
    rmd = []
    for item in items:
        if not NON_ALPHA.search(item):
            rmd.append(item)
    return rmd


def to_csv(data, path):
    with open(path, 'wb') as wrt:
        wrtr = csv.writer(wrt, quoting=csv.QUOTE_MINIMAL)
        for row in data:
            wrtr.writerow(tuple([encode(field) for field in row]))


def from_csv(path):
    with open(path, 'rb') as rd:
        rdr = csv.reader(rd)
        for row in rdr:
            yield row
