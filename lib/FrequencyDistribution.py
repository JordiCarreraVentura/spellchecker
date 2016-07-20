

from collections import (
    Counter,
    defaultdict as deft
)

from TermIndex import TermIndex

from Tools import to_csv as _to_csv


class FrequencyDistribution:


    def __init__(self, iterable=None):
        self.frequencies = Counter()
        self.mass = 0.0
        self.ranks = None
        if iterable:
            self(iterable)


    def __call__(self, iterable):
        for tokens in iterable:
            self.frequencies.update(tokens)
            self.mass += len(tokens)

    
    def probability(self, w):
        f = self.frequencies[w]
        if w:
            return f / self.mass
        else:
            return 0.0

    def prob(self, w):
        f = self.frequencies[w]
        if w:
            return f / self.mass
        else:
            return 0.0
    
    
    def frequency(self, w):
        return self.frequencies[w]


    def __getitem__(self, w):
        return self.frequencies[w]
    
    
    def __iter__(self):
        for word, freq in self.frequencies.items():
            yield word, freq
    
    
    def __add__(self, dist):
        for w, f in dist:
            self.frequencies[w] += f
            self.mass += f
    
    
    def __sub__(self, dist):
        sub = FrequencyDistribution()
        freqs = Counter()
        for w, _ in self:
            _p = self.prob(w) - dist.prob(w)
            _p = -(self.rank(w) - dist.rank(w))
            if _p < 0:
                _p = 0
            freqs[w] = _p
        sub.frequencies = freqs
        return sub


    def __and__(self, dist):
        sub = FrequencyDistribution()
        freqs = Counter()
        for w, _ in self:
#             _p = self.prob(w) - dist.prob(w)
            _p = 100 / (self.rank(w) + dist.rank(w) + 0.1)
            freqs[w] = _p
        sub.frequencies = freqs
        return sub
    
    
    def rank(self, w):
        f = self[w]
        if not f:
            return 100
        if not self.ranks:
            self.__ranks()
        return self.ranks[f]
    
    
    def __ranks(self):
        vv = sorted(set(self.frequencies.values()), reverse=True)
        self.ranks = dict([])
        for i, v in enumerate(vv):
            _i = int((i + 1) / float(len(vv)) * 100)
            self.ranks[v] = _i


    def top(self, n=10):
        return self.frequencies.most_common(n)
    
    
    def content(self):
        return []
            
        

#     def to_csv(self):
#         self.words.to_csv()
#         rows = []
#         for _id, vector in self.vectors.items():
#             row = [_id] + ['%d=%d' % (i, f) for i, f in vector.items()]
#             if row[1:]:
#                 rows.append(row)
#         _to_csv(rows, 'vector.index.csv')
