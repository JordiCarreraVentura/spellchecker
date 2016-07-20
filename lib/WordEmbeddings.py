import gensim

from collections import (
    Counter,
    defaultdict as deft
)

from multiprocessing import cpu_count

from tqdm import tqdm


class WordEmbeddings:
    
    def __init__(
        self,
        dimensions=100,
        window=5,
        min_count=1,
        workers=1,
#         workers=cpu_count(),
        max_vocab_size=20000000,
        iter=5,
        sg=0
    ):
        self.dimensions = dimensions
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.max_vocab_size = max_vocab_size
        self.iter = iter
        self.sg = sg
        self.model = None
        self.observed = deft(bool)
    
    def train(self, iterable):
        self.model = gensim.models.Word2Vec(
            iterable,
            size=self.dimensions,
            window=self.window,
            min_count=self.min_count,
            workers=self.workers,
            max_vocab_size=self.max_vocab_size,
            iter=self.iter,
            sg=self.sg
        )
    
    def compile(self):
        for w in self:
            self.observed[w] = True
    
    def __iter__(self):
        for w in self.model.vocab.keys():
            yield w

    def similar(self, w, n=10, r=0.0):
        return [
            (w, sim)
            for w, sim in self.model.most_similar(positive=[w])
            if sim >= r
        ][:n]
    
    def similarity(self, w, v):
        return self.model.similarity(w, v)
