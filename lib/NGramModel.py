
from tqdm import tqdm

from Tools import ngrams

from collections import (
    Counter,
    defaultdict as deft
)

from TermIndex import TermIndex


class NGramModel:
    
    def __init__(
        self,
        stream,
        ngrams=[
            (1, False),
            (2, False),
            (3, False),
            (4, False),
            (5, False),
            (3, True),
            (4, True),
            (5, True)
        ],
        min_f=2,
        ratio_within=0.8,
        transversal_filter=deft(bool),
        wrapping_filter=deft(bool)
    ):
        self.min_f = min_f
        self.ratio_within = ratio_within
        self.words = TermIndex('')
        self.ngrams = ngrams
        self.stream = stream
        self.priors = Counter()
        self.mass = 0.0
        self.posteriors = deft(Counter)
        self.masses = deft(float)
        self.skipped = deft(Counter)
        self.skippers = deft(Counter)
        self.transversal_filter = transversal_filter
        self.wrapping_filter = wrapping_filter
        self.rewrites = deft(tuple)
        self.relations = Counter()
        self.relaheads = Counter()

    def train(self):
        for words in self.stream:
            tokens = [self.words(w) for w in words]
            self.priors.update(tokens)
            self.mass += len(tokens)
            for n, skip in self.ngrams:
                _grams = list(ngrams(tokens, n))
                _grams = self.__transversal_filter(_grams)
                if skip:
                    _grams = self.__skip(_grams)
                self.masses[n] += len(_grams)
                self.posteriors[(n, skip)].update(_grams)

    def __skip(self, _grams):
        skipped = []
        for g in _grams:
            skipping = (g[0], g[-1])
            _skipped = tuple(g[1:-1])
            self.skipped[skipping][_skipped] += 1
            self.skippers[_skipped][skipping] += 1
            skipped.append(skipping)
        return skipped

    def __transversal_filter(self, _grams):
        new = []
        for g in _grams:
            if not [w for w in g if self.transversal_filter[self.words[w]]]:
                new.append(g)
        return new

    def extract(self, merge=True):
        nn = sorted([n for n, skip in self.ngrams if not skip], reverse=True)
        snn = sorted([n for n, skip in self.ngrams if skip], reverse=True)
        covered = deft(bool)
        accepted = []
        for n in [5, 4, 3, 2]:
            if n <= 1:
                break
            for gids, freq in tqdm(self.posteriors[(n, False)].items()):

                if freq < self.min_f:
                    continue

                if not self.__wrapping_filter(gids):
                    continue

                pxy = freq / self.masses[n]
                fx = self.posteriors[(n - 1, False)][gids[:n - 1]]
                fy = self.posteriors[(n - 1, False)][gids[-(n - 1):]]
                px = fx / self.masses[n - 1]
                py = fy / self.masses[n - 1]
                px_y = px * py
                
                gxy = [self.words[i] for i in gids]
                gx = [self.words[i] for i in gids[:n - 1]]
                gy = [self.words[i] for i in gids[-(n - 1):]]
                
                if covered[gids]:
                    continue

                if (pxy >= px * self.ratio_within and pxy >= py * self.ratio_within):
                    _n = n - 1
                    self.rewrites[tuple(gxy)] = tuple(gxy)
                    while _n:
                        _gids = gids[:_n]
                        gids_ = gids[_n:]
                        covered[_gids] = True
                        covered[gids_] = True
                        _n -= 1

        self.__inside_extract()
    
    
    def __inside_extract(self):
        for n in [5, 4, 3]:
            processed = deft(bool)
            posteriors = [
                (gids, freq) for gids, freq in self.posteriors[(n, False)].items()
                if freq > 4
            ]
            for gids, freq in tqdm(posteriors):
                self.__extract_relations(processed, n, gids, freq)
#                 print [([self.words[y] for y in yy], f) for yy, f in self.relations.most_common(20)]
#                 print
    
    def __extract_relations(self, processed, n, gids, freq):

        abstr = (gids[0], gids[-1])
        if processed[abstr]:
           return
        
        processed[abstr] = True
        _n = n
        while _n >= len(gids):
            _n -= 1
            insides = self.skipped[abstr]
            
#             print [self.words[i] for i in gids], freq, freq / self.masses[n]
            for x, f in insides.most_common():
                if f < 2:
                    break

                inside = [self.words[j] for j in x]
#                 print '\t', inside, f, f / self.masses[len(x)]
                skippers = []
                for _x, _f in self.skippers[x].most_common():
                    if _f >= f and \
                    self.__transversal_filter([_x]) and \
                    self.__wrapping_filter([_x]):
                        skippers.append((_x, _f))
                for _x, _f in skippers:
                    outside = [self.words[j] for j in _x]
                    relation = tuple([_x[0]] + list(x) + [_x[-1]])
                    #relation = x
                    self.relations[relation] += 1
#                         print '\t\t', outside[0], inside, outside[-1], _f, relation

        for relation, freq in self.relations.most_common():
            if freq >= 3:
                rel = tuple([self.words[j] for j in relation])
                self.rewrites[rel] = relation

    
    def rewrite(self, content=None):
#         if content:
#             for w, boolean in content.items():
#                 if boolean:
#                     self.rewrites[tuple([w])] = True
        for words in self.stream:
            rwrt = []
            for n in sorted(set([n for n, _ in self.ngrams]), reverse=True):
                rwrt += [g for g in ngrams(words, n) if self.rewrites[g]]
            if rwrt:
                print words
                print rwrt
                print


    def __wrapping_filter(self, g):
        if (
            len(g) > 1 and
            not self.wrapping_filter[self.words[g[0]]] and
            not self.wrapping_filter[self.words[g[-1]]]
        ):
            return True
        else:
            return False

#         nn, skips = zip()
#         for i, n in enumerate(nn):
#             print n, skips[i]
        
