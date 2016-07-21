from __future__ import division


import math
import os
import sys
import time

from config import CONFIG

from tests import tests1, tests2

from normalizer import Normalizer

from lib.CharacterIndex import CharacterIndex
from lib.NaiveTokenizer import NaiveTokenizer
from lib.TextStreamer import TextStreamer
from lib.CONLL14ErrorCorrection import CONLL14ErrorCorrection
from lib.Report import Report

from lib.Tools import (
    FreqDist,
    splitter,
    strip_punct,
    tokenizer
)

from collections import (
    Counter,
    defaultdict as deft
)


def timestamp():
    return '.'.join([str(t) for t in time.localtime()[3:6]])


def get_name(template):
    i = 1
    while True:
        name = template % (timestamp(), i)
        if not os.path.exists(name):
            return name
        i += 1



corpus = 'data/delorme.com_shu.pages_89.txt'

report = Report()

for C in CONFIG:
    
#     tests = tests1.items() + tests2.items()

    conll = CONLL14ErrorCorrection()
    
    tests = []
    for (left, err, right, corr, category), human  in conll:
        if err:
            test = (left, strip_punct(err).lower(), right,
                    strip_punct(corr).lower(), category, True)
        else:
            test = (left, strip_punct(corr), right, err, category, False)
        tests.append(test)
    tests = tests

    targets = [test[1] for test in tests]

    #	Collect input from large text file:
    dump = []
    for doc in TextStreamer(corpus, nb_sent=C['nb_sent']):
        for sent in splitter(doc):
            dump += [w.lower() for w in tokenizer(sent)]
    freq_dist = Counter(dump + targets)

    #	Map all character n-grams to words, and all words to their
    #	character n-grams
    index = CharacterIndex(dump + targets, top_n=C['top_n'], min_r=C['sim_thres'])
    index.build()

    for left, error, right, correct, category, human in tests:
        
        if error == correct:
            continue

        report.add()

        if human:
            left = ' '.join(left.split()[-10:])
            right = ' '.join(right.split()[:10])
        else:
            left = ''
            right = ''

        similars = [(w, sim) for w, sim in index[error]
                    if freq_dist[w] >= 10 and
                    freq_dist[w] / freq_dist[error] >= 30]

        if not similars and not human:
            report.tn(left, error, right, correct, category)
            continue
        elif not similars:
            report.fn(left, error, right, correct, category)
            continue
        elif similars and not human:
            report.fp(left, error, right, correct, category)
            continue

        similars.sort(
            key=lambda x: freq_dist[x[0]],
            reverse=True
        )

        top = [w for w, _ in similars[:1]]
        if correct in top:
            report.tp(left, error, right, correct, category)
        else:
            report.fp(left, error, right, correct, category)
    
    report.lap(C)


template = 'logs/test-%s-%d'
report(get_name(template))
