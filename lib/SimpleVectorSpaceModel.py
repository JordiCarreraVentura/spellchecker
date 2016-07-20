
import random

from tqdm import tqdm

from collections import (
    Counter,
    defaultdict as deft
)

from Tools import STOPWORDS

from random import shuffle as randomize

from TermIndex import TermIndex



class SimpleVectorSpaceModel:

    def __init__(
        self,
        streamer,
        window=5,
        n=1000,
        prune_at=5000
    ):
        self.streamer = streamer
        self.window = window
        self.n = n
        self.prune_at = prune_at
        self.words = TermIndex('')
        self.features = TermIndex('')
        self.mass = 0.0
        self.cc_by_w = deft(list)
        self.qq_by_w = dict([])
        self.post_mass = deft(float)
        self.priors = Counter()
        self.ww_by_f = deft(set)
        self.ff_by_w = deft(set)
        self.types = deft(str)
    
    def __frame(self, i, tokens):
        start = i - self.window
        end = i + self.window + 1
        left, right = [], []
        if start > 0:
            left = tokens[start:i]
        else:
            left = tokens[:i]
        if end < len(tokens):
            right = tokens[i + 1:end]
        else:
            right = tokens[i + 1:]
        return left, right
    
    
    def extract(self):
        ff = Counter()
        from lib.Tools import ngrams
        for w, cc in tqdm(self.cc_by_w.items()):
#             w = self.words[_w]
            features = []
            for c in cc:
#                 c = [self.words[x] for x in c]
                left, right = c[:self.window], c[-self.window:]
                
                f = ('2_x', tuple(left[-2:]))
                self.__add_feature(ff, w, f)
                
                f = ('3_x', tuple(left[-3:]))
                self.__add_feature(ff, w, f)
                
                f = ('1_x', tuple(left[-1:]))
                self.__add_feature(ff, w, f)
                
                f = ('x_2', tuple(right[:2]))
                self.__add_feature(ff, w, f)
                
                f = ('x_3', tuple(right[:3]))
                self.__add_feature(ff, w, f)
                
                f = ('x_1', tuple(right[:1]))
                self.__add_feature(ff, w, f)

                g11 = (left[-1], right[0])
                g12 = (left[-1], right[0], right[1])
                g21 = (left[-2], left[-1], right[0])
                if not [token for token in g11 if self.words[token].isupper()]:
                    f = ('1_x_1', g11)
                    self.__add_feature(ff, w, f)
                if not [token for token in g12 if self.words[token].isupper()]:
                    f = ('1_x_2', g12)
                    self.__add_feature(ff, w, f)
                if not [token for token in g21 if self.words[token].isupper()]:
                    f = ('2_x_1', g21)
                    self.__add_feature(ff, w, f)

        votes = Counter()
        for fid, freq in tqdm(ff.most_common()):
            if freq < 3:
                break
            words = self.ww_by_f[fid]
            y, z = self.features[fid]
            
            for w in words:
                for v in words:
                    if w == v:
                        continue
                    votes[(w, v)] += (1 / float(freq)) * len(words)

        for (w, v), freq in votes.most_common():
            if freq < 10:
                break
            a, b = self.words[w], self.words[v]
            if not (a.isupper() or b.isupper()):
                continue
            if a.isupper() and b.islower() and b not in self.types.keys():
                self.types[b] = a
                print '%s IS_A %s' % (b, a)
            elif b.isupper() and a.islower() and a not in self.types.keys():
                self.types[a] = b
                print '%s IS_A %s' % (a, b)


    def __add_feature(self, ff, w, f):
#         if [token for token in f if self.words[token].isupper()]:
#             return
        fid = self.features(f)
        word = self.words[w]
        if STOPWORDS[word] or not word.isalpha():
            return
        if ff[fid] >= 5000 or len(self.ww_by_f[fid]) >= 1500:
            try:
                del self.ff_by_w[w]
                del self.ww_by_f[fid]
                del ff[fid]
                self.features.drop(fid)
            except Exception:
                pass
            return
        ff[fid] += 1
        self.ff_by_w[w].add(fid)
        self.ww_by_f[fid].add(w)


    def train(self):
        for i, tokens in enumerate(self.streamer):
            self.update(tokens)
            self.__prune(i)
        self.__compute()
        self.extract()

        
    def __compute(self):
        for w, cc in self.cc_by_w.items():
            dump = []
            for c in cc:
                dump += c
            counts = Counter(dump)
            self.qq_by_w[w] = counts
            self.post_mass[w] += float(sum(counts.values()))
    
    def __prune(self, i):
        if i and i % self.prune_at:
            return
        for w, cc in tqdm(self.cc_by_w.items()):
            if len(cc) < self.n * 2:
                continue
            randomize(cc)
            self.cc_by_w[w] = cc[:self.n]
#             print w, len(cc), len(self.cc_by_w[w])

    
    def __getitem__(self, w):

        if not self.words.known(w):
            return None

        wid = self.words.ids[w]
        mass = self.post_mass[wid]
        if not mass:
            return None

        return {
            _w: (fxy / mass) * ((fxy / mass) / (self.priors[_w] / self.mass))
            for _w, fxy in self.qq_by_w[wid].items()
        }


    def similarity(self, w, v):
        bow_w = self[w]
        bow_v = self[v]
        if not (bow_w and bow_v):
            return 0.0
        else:
            return self.__sim(bow_w, bow_v)
    
    def __sim(self, bow_w, bow_v):
        sum_w, sum_v = 0.0, 0.0
        ref_w = float(sum(bow_w.values()))
        ref_v = float(sum(bow_v.values()))
        common = [self.words[x] for x in set(bow_w.keys()).intersection(set(bow_v.keys()))]
        for i in set(bow_w.keys()).intersection(set(bow_v.keys())):
            sum_w += bow_w[i] / ref_w
            sum_v += bow_v[i] / ref_v
#         print common
#         print sum_w / ref_w, sum_v / ref_v
#         print '----'
        return sum_w
    
    def __iter__(self):
        for w in self.words:
            yield w
#         for w, cc in self.cc_by_w.items():
#             mass = self.post_mass[w]
#             weighted = [
#                 (self.words[w],
#                 (fxy / mass) * ((fxy / mass) / (self.priors[w] / self.mass)))
#                 for w, fxy in self.qq_by_w[w].items()
#             ]
#             print self.words[w], sorted(weighted, key=lambda x: x[1], reverse=True)[:50]
#             raw_input()
    
    def update(self, tokens):
        for i, w in enumerate(tokens):
            wid = self.words(w)
            self.priors[wid] += 1
            left, right = self.__frame(i, tokens)
            if left and right:
                cwids = [self.words(cw) for cw in left + right]
                self.mass += 1
                self.cc_by_w[wid].append(cwids)
