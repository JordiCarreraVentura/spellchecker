
import numpy as np
import scipy

from collections import (
    Counter,
    defaultdict as deft
)

from copy import deepcopy as cp

from scipy.spatial.distance import cosine

from TermIndex import TermIndex

from Tools import ngrams


class SimpleHiddenMarkovModel:

    def __init__(
        self,
        streamer,
        nn=[1, 2, 3]
    ):
        self.nn = nn
        self.streamer = streamer
        self.words = TermIndex('words')
        self.lefts = deft(Counter)
        self.rights = deft(Counter)
        self.orders = dict([])
        for n in self.nn:
            self.orders[n] = deft(Counter)
            self.orders[-n] = deft(Counter)
        self.mass = deft(float)
        self.priors = Counter()
    
    def train(self):
        for tokens in self.streamer:
            ids = [self.words(token) for token in tokens]
            for i, center in enumerate(ids):
                self.priors[center] += 1
                for n in self.nn:
                    self.mass[n] += 1
                    self.mass[-n] += 1
                    left = i - n
                    if left > 0:
                        li = ids[left]
                        #print 'left', i, -n, self.words[center], left, self.words[li]
                        self.orders[-n][center][li] += 1
                        self.orders[-n][center]['*'] += 1
                    right = i + n
                    if right < len(tokens):
                        ri = ids[right]
                        #print 'right', i, n, self.words[center], right, self.words[ri]
                        self.orders[n][center][ri] += 1
                        self.orders[n][center]['*'] += 1


    def similarity(self, _w, _v):
        
        w = self.words(_w)
        v = self.words(_v)
        weights_w = dict([])
        weights_v = dict([])
        for n in self.nn:

            weights_w.update({
#                 (n, feature): (weight / self.mass[n]) * (1 / float(n))
                (n, feature): (weight / float(self.orders[n][w]['*'])) * (1 / float(n))
#                 (n, feature): ((weight / float(self.orders[n][w]['*'])) / (self.priors[feature] / self.mass[n])) * (1 / float(n))
                for feature, weight in self.orders[n][w].items()
                if feature != '*'
            })
            
            weights_w.update({
#                 (-n, feature): (weight / self.mass[-n]) * (1 / float(n))
                (-n, feature): (weight / float(self.orders[-n][w]['*'])) * (1 / float(n))
#                 (-n, feature): ((weight / float(self.orders[-n][w]['*'])) / (self.priors[feature] / self.mass[-n])) * (1 / float(n))
                for feature, weight in self.orders[-n][w].items()
                if feature != '*'
            })
            
            weights_v.update({
#                 (n, feature): (weight / self.mass[n]) * (1 / float(n))
                (n, feature): (weight / float(self.orders[n][v]['*'])) * (1 / float(n))
#                 (n, feature): ((weight / float(self.orders[n][v]['*'])) / (self.priors[feature] / self.mass[n])) * (1 / float(n))
                for feature, weight in self.orders[n][v].items()
                if feature != '*'
            })

            weights_v.update({
#                 (-n, feature): (weight / self.mass[-n]) * (1 / float(n))
                (-n, feature): (weight / float(self.orders[-n][v]['*'])) * (1 / float(n))
#                 (-n, feature): ((weight / float(self.orders[-n][v]['*'])) / (self.priors[feature] / self.mass[-n])) * (1 / float(n))
                for feature, weight in self.orders[-n][v].items()
                if feature != '*'
            })

        sum_w, sum_v = 0.0, 0.0
        ref_w, ref_v = float(sum(weights_w.values())), float(sum(weights_v.values()))
        common = [self.words[y] for x, y in set(weights_w.keys()).intersection(set(weights_v.keys()))]
#         print
#         print common
        for x, y in set(weights_w.keys()).intersection(set(weights_v.keys())):
#             print self.words[w], x, self.words[y], weights_w[(x, y)]
#             print self.words[v], x, self.words[y], weights_v[(x, y)]
            sum_w += weights_w[(x, y)] / ref_w
            sum_v += weights_v[(x, y)] / ref_v
#         print sum_w, sum_v
#
        return sum_w


    def cosine_similarity(self, _w, _v):
        
        w = self.words(_w)
        v = self.words(_v)
        weights_w = dict([])
        weights_v = dict([])
        for n in self.nn:

            weights_w.update({
#                 (n, feature): (weight / self.mass[n]) * (1 / float(n))
                (n, feature): (weight / float(self.orders[n][w]['*'])) * (1 / float(n))
#                 (n, feature): ((weight / float(self.orders[n][w]['*'])) / (self.priors[feature] / self.mass[n])) * (1 / float(n))
                for feature, weight in self.orders[n][w].items()
                if feature != '*'
            })
            
            weights_w.update({
#                 (-n, feature): (weight / self.mass[-n]) * (1 / float(n))
                (-n, feature): (weight / float(self.orders[-n][w]['*'])) * (1 / float(n))
#                 (-n, feature): ((weight / float(self.orders[-n][w]['*'])) / (self.priors[feature] / self.mass[-n])) * (1 / float(n))
                for feature, weight in self.orders[-n][w].items()
                if feature != '*'
            })
            
            weights_v.update({
#                 (n, feature): (weight / self.mass[n]) * (1 / float(n))
                (n, feature): (weight / float(self.orders[n][v]['*'])) * (1 / float(n))
#                 (n, feature): ((weight / float(self.orders[n][v]['*'])) / (self.priors[feature] / self.mass[n])) * (1 / float(n))
                for feature, weight in self.orders[n][v].items()
                if feature != '*'
            })

            weights_v.update({
#                 (-n, feature): (weight / self.mass[-n]) * (1 / float(n))
                (-n, feature): (weight / float(self.orders[-n][v]['*'])) * (1 / float(n))
#                 (-n, feature): ((weight / float(self.orders[-n][v]['*'])) / (self.priors[feature] / self.mass[-n])) * (1 / float(n))
                for feature, weight in self.orders[-n][v].items()
                if feature != '*'
            })

        dimensions = list(set(weights_w.keys()).union(set(weights_v.keys())))
        vector_w = self.__getvec(dimensions, weights_w)
        vector_v = self.__getvec(dimensions, weights_v)

        return cosine(vector_w, vector_v)


    def __getvec(self, dimensions, weights):
        vec = dict([])
        for dimension in dimensions:
            vec[dimension] = 0.0
        for feature, weight in weights.items():
            vec[feature] += weight
        return np.array([vec[w] for w in dimensions])
        
        
