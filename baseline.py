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
from lib.Parser import PatternParser
from lib.Report import Report
from lib.DistributionalModel import NgramModel

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

PoS_l = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT',
         'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP',
         'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
PoS = {}
i = 1
for k in PoS_l:
    PoS[k] = i
    i += 1


WORD_GRAMS = [
    (1, False),
    (2, False),
    (3, False),
    (3, True),
    (4, True)
]

POS_GRAMS = [
    (1, False),
    (2, False),
    (3, False),
#     (3, True),
#     (4, True)
]



corpus1 = 'data/delorme.com_shu.pages_89.txt'
corpus2 = 'data/delorme.com_shu.pages_102.txt'
corpus3 = 'data/delorme.com_shu.pages_120.txt'
corpus4 = 'data/utexas_iit.pages_12.txt'

report = Report()

parser = PatternParser()

model = NgramModel(WORD_GRAMS)
model_pos = NgramModel(POS_GRAMS)

C = CONFIG[1]




 #for C in CONFIG:
    
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
tests = tests[:30000]

targets = [test[1] for test in tests]


#    Collect input from large text file:
dump = []
#     for doc in TextStreamer(corpus, nb_sent=C['nb_sent']):
streamers = [
    TextStreamer(corpus1, nb_sent=200000),
    TextStreamer(corpus2, nb_sent=200000),
    TextStreamer(corpus3, nb_sent=200000),
    TextStreamer(corpus4, nb_sent=200000),
]
for streamer in streamers:
    for doc in streamer:
        for sent in splitter(doc):

            tokenized = [w.lower() for w in tokenizer(sent)]
            dump += tokenized

#             parse = parser(sent)
#             tok_pos = [pos[1] for pos in parse.split()[0]]
            model.update(['#'] + tokenized + ['#'])
#             model_pos.update(['#'] + tok_pos + ['#'])

freq_dist = Counter(dump + targets)



#    Map all character n-grams to words, and all words to their
#    character n-grams
#    index = CharacterIndex(dump + targets, top_n=C['top_n'], min_r=C['sim_thres'])
index = CharacterIndex(dump + targets, top_n=C['top_n'], min_r=C['sim_thres'])
index.build()

tests = [t for t in tests]
for i, (left, candidate, right, correct, category, is_candidate) in enumerate(tests):
    
    if candidate == correct:
        continue
#         elif is_candidate and (category != 'Mec'):
#             continue
#        if candidate in ['diagonosed','firghtenning','concurently']:

    report.add()

    if is_candidate and ((not correct or len(correct.split()) > 1)
    or category not in ['Mec']):
#         or category not in ['Mec', 'Nn', 'Wform']):
        report.fn(left, candidate, right, correct, category)
        continue

#         similars = index(candidate, n=5)
    similars = [(w, sim) for w, sim in index(candidate)
                if freq_dist[w] >= 10 and
                freq_dist[w] / freq_dist[candidate] >= 100]

    if not similars and not is_candidate:
        report.tn(left, candidate, right, correct, category)
        continue
    elif not similars:
        report.fn(left, candidate, right, correct, category)
        continue
    elif similars and not is_candidate:
        report.fp(left, candidate, right, correct, category)
        continue

#         similars.sort(
#             key=lambda x: freq_dist[x[0]],
#             reverse=True
#         )
#         top = [w for w, sim in similars[:1]]

    corrections = []
    for sim, _ in similars + [(candidate, None)]:
        left = [e.strip() for _, e, _, _, _, _ in tests[i - 3:i]] + [sim]
        right = [sim] + [e.strip() for _, e, _, _, _, _ in tests[i + 1:i + 4]]

        pos_context_left = ' '.join([e for _, e, _, _, _, _ in tests[i - 3:i]] 
                               + [sim])
        pos_context_right = ' '.join([sim]
                               + [e for _, e, _, _, _, _ in tests[i + 1:i + 4]])

#         parse_pos_left = parser(pos_context_left)
#         parse_pos_right = parser(pos_context_right)

#         left_pos = [e_pos[1] for e_pos in parse_pos_left.split()[0]]
#         right_pos = [e_pos[1] for e_pos in parse_pos_right.split()[0]]

#         pleft_pos = model_pos(left_pos)
#         pright_pos = model_pos(right_pos)
        pleft_pos = 0.0
        pright_pos = 0.0
        
        
        pleft = model(left)
        pright = model(right)

        score = abs(pleft - pright)
        score_pos = abs(pleft_pos - pright_pos)

        print left
        print '... %s' % right
        print candidate, '/%s' % correct
        print 'grams |', ' '.join(left), pleft
        print 'grams |', ' '.join(right), pright
        print 'pos |', '', pleft_pos
        print 'pos |', '', pright
        print 

#         corrections.append((score * max([pleft, pright]), score_pos * max([pleft_pos, pright_pos]), sim))
        corrections.append((max([pleft, pright]), max([pleft_pos, pright_pos]), sim))

    baseline = [[sim_w, sim_pos, w] for sim_w, sim_pos, w in corrections if w == candidate][0]
    #top = [w for sim_w, sim_pos, w in corrections if w == candidate][0]
    #         print [(freq_dist[w] / freq_dist[candidate], w) for sim, w in corrections[:1]
    #                    if freq_dist[w] / freq_dist[candidate] >= 2]
    #         print [w for sim, w in corrections[:1]
    #                    if (baseline and sim / baseline >= 2)
    #                    or not baseline]
    #         print

    #print corrections

    #hypothesis = [sim_w, sim_pos, w in corrections[:1] if w != candidate]
    #        top_w = [w for sim_w, sim_pos, w in corrections[:1] if w != candidate]
    #        top_sim_w = [sim_w for sim_w, sim_pos, w in corrections[:1] if w != candidate]
    #        top_sim_pos = [sim_pos for sim_w, sim_pos, w in corrections[:1] if w != candidate]

    is_corrected = False
    for hyp in corrections:
        if hyp[0] >= baseline[0] and hyp[1] >= baseline[1]:
            baseline = hyp
            is_corrected = True
    top = baseline[2]

    if not is_corrected and is_candidate:
        report.fn(left, candidate, right, correct, category)
    elif not is_corrected and not is_candidate:
        report.tn(left, candidate, right, correct, category)
    elif is_candidate and correct == top:
        report.tp(left, candidate, right, correct, category)
    elif is_corrected and not is_candidate:
        report.fp(left, candidate, right, correct, category)

report.lap(C)

template = 'logs/test-%s-%d'
report(get_name(template))

