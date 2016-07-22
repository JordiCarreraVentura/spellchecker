from __future__ import division

import nltk
import math

from collections import (
    Counter,
    defaultdict as deft
)

# from FeatureFunctions import *

from TermIndex import TermIndex

from nltk import ngrams


def prod(probs):
    if not probs:
        return 0.0
    _prod = probs[0]
    for prob in probs:
        _prod *= prob
    return _prod



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
    (3, False)
]



class NgramModel:

    def __init__(self, n):
        self.n = n
        self.index = TermIndex('')
        self.data = deft(Counter)
        self.mass = Counter()
    
    def update(self, tokens):
        for n, skip, gram in self.grams(tokens):
            self.data[(n, skip)][gram] += 1
            self.mass[(n, skip)] += 1

    def grams(self, seq):
        for n, skip in self.n:
            if n > seq:
                continue
            for gram in ngrams(seq, n):
                if skip:
                    gram = (gram[0], gram[-1])
                gram = self.index(gram)
                yield n, skip, gram
    
    def __call__(self, window):
        probs = deft(list)
        for n, skip, gram in self.grams(window):
            prob = self.data[(n, skip)][gram] / self.mass[(n, skip)]
#             print n, skip, self.index[gram], '\t', self.data[(n, skip)][gram], self.mass[(n, skip)]
#             if not prob:
#                 prob = 0.5 / self.mass[(n, skip)]
#             probs[(n, skip)].append(math.log(prob, 10))
            probs[(n, skip)].append(prob)
#         print probs
        
        scores = dict([])
        for (n, skip) in [(3, False), (2, False), (3, True), (4, True), (1, False)]:
            prob = prod(probs[(n, skip)])
            if prob:
                return prob
        return 0.0



if __name__ == '__main__':

    data = [
        (1, 1, 1, 2),
        (1, 1, 1, 3),
        (1, 1, 1, 4),
        (1, 2),
        (1, 2, 1, 2)
    ]

    tests = [
        (1, 1, 1),
        (1, 2),
        (4, 1)
    ]

    model = NgramModel(WORD_GRAMS)
    for record in data:
        model.update(['#'] + list(record) + ['#'])
        #model.update(list(record))

    for test in tests:
        print test
        print model(test)
    
#         scores = []
#         for (n, skip), probs in model(['#'] + list(test) + ['#']).items():
#             score = prod(probs)
#             scores.append(score)
#             print n, skip, score
#         print sum(scores)
#         print


# 
# class DistributionalModel:
#     
#     def __init__(self):
#         self.index = TermIndex('')
#         self.fx = Counter()
#         self.left = deft(Counter)
#         self.right = deft(Counter)
#         self.mass = Counter()
#     
#     def update(self, sentence):
#         words, pos, lemmas = zip(*sentence)
#         for i, w in enumerate(words):
#             
#             for n, skip in NGRAMS:
#                 self.__leftgram(n, skip, i, w, words)
#             
#             for n, skip in NGRAMS:
#                 self.__rightgram(n, skip, i, w, words)
#             
#             self.__prepos(i, pos)
#             self.__postpos(i, pos)
# 
#     
#     def __prepos(self, i, pos):
#         if i < len(pos) - 2:
#             pos1, pos2 = pos[i - 2:i]
#             pos12 = (pos1, pos2)
#             ij = self.index(pos12)
#             j = self.index(pos2)
#             self.left[ij] += 1
#             self.left[j] += 1
#             self.mass[('pos', 2)] += 1
#             self.mass[('pos', 1)] += 1
#         elif i < len(pos) - 1:
#             pos1 = pos[i - 1]
#             i = self.index(pos1)
#             self.left[i] += 1
#             self.mass[('pos', 1)] += 1
#         return
#             
            
#     def __leftgram(self, n, skip, i, w, words):
#         
#         
#             word_1 = words
#             
#             left = [w for w in sentence[:i]]
#             right = [w for w in sentence[i + 1:]]
#             if left:
#                 self.add(False, i, w, sentence, left)
#             else:
#                 self.add(True, i, w, sentence, right)
#     
#     def add(self, side, i, w, sentence, context):
#         if not side:
#             
