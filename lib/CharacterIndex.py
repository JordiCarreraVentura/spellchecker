
import difflib

from collections import (
    Counter,
    defaultdict as deft
)

from difflib import SequenceMatcher as fuzzmatch

from TermIndex import TermIndex

from Tools import ngrams


class CharacterIndex:

    def __init__(self, streamer, top_n=100, min_r=0.9):
        self.streamer = streamer
        self.words = TermIndex('')
        self.ww_by_ch = deft(list)
        self.top_n = top_n
        self.min_r = min_r

    def build(self):
        for tokens in self.streamer:
            for w in tokens:
                self.add(w)
        self.__compile()
    
    def __compile(self):
        for w, ii in self.ww_by_ch.items():
            self.ww_by_ch[w] = set(ii)

    def add(self, w):
        if self.words.known(w):
            return
        _id = self.words(w)
        for g in self.grams(w):
            self.ww_by_ch[g].append(_id)
    
    def grams(self, w):
        _w = '#%s#' % w
        for g in ngrams(_w, 2):
            yield ''.join(g)


    def __call__(self, w, n=5):

        hits = Counter()
        grams = self.grams(w)
        reference = 0.0
        for g in grams:
            hits.update(self.ww_by_ch[g])
            reference += 1

        candidates = sorted(
            [(self.words[i], f)
             for i, f in hits.most_common(self.top_n)
             if self.words[i] != w],
            key=lambda x: x[1] / max([reference, float(len(list(self.grams(x[0]))))]),
            reverse=True
        )

        hypotheses = []
        for c, _ in candidates:
            r = fuzzmatch(None, w, c).ratio()
            if r < self.min_r:
                continue
            hypotheses.append((c, r))

        return sorted(
            hypotheses,
            key=lambda x: x[1],
            reverse=True
        )[:n]


    def __iter__(self):
        for w in self.words:
            yield (w, self(w))


    def __getitem__(self, w):
        return self(w)
    
        

