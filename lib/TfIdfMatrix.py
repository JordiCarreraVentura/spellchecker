
import math

from collections import (
    Counter,
    defaultdict as deft
)


from Tools import from_csv


class TfIdfMatrix:
    
    def __init__(self, max_df=20000):
        self.df = Counter()
        self.tf = dict([])
        self.docs = 0.0
        self.mass = 0.0
        self.dmass = deft(float)
        self.word_by_id = dict([])
        self.id_by_word = dict([])
        self.max_df = max_df
    
    def load_features(self, path):
        for word, _id in from_csv(path):
            _id = int(_id)
            self.word_by_id[_id] = word
            self.id_by_word[word] = _id
    
    def load_distribution(self, path):
        for row in from_csv(path):
            _id = int(row[0])
            counts = dict([])
            for field in row[1:]:
                term, freq = field.split('=')
                term = int(term)
                freq = int(freq)
                counts[term] = freq
                self.df[term] += 1
                self.mass += freq
                self.dmass[_id] += freq
                self.docs += 1
            self.tf[_id] = counts
    
    def idf(self, _id, word):
        return math.log(self.docs / self.df[word], 10)
    
    def mi(self, _id, w_id):
        px = self.df[w_id] / self.docs
        pxy = self.tf[_id][w_id] / self.dmass[_id]
#         print w_id, self.word_by_id[w_id], px, pxy, '\t', pxy * (pxy / px)
        return pxy * (pxy / px)

    def tfidf(self, _id, w_id):
        tf = self.tf[_id][w_id]
        idf = self.idf(_id, w_id)
        print w_id, self.word_by_id[w_id], tf, idf, '\t', tf * idf
        return tf * idf
    
    def content(self, _id):
        if _id == None:
            return []
        try:
            out = []
            for w_id in self.tf[_id].keys():
                if self.df[w_id] >= self.max_df:
                    continue
#                 out.append((self.word_by_id[w_id], self.tfidf(_id, w_id)))
#                 out.append((self.word_by_id[w_id], self.mi(_id, w_id)))
                out.append((w_id, self.mi(_id, w_id)))
#                 out.append((self.word_by_id[w_id], self.tf[_id][w_id]))
            return sorted(out, key=lambda x: x[1], reverse=True)
        except Exception:
            return []
