import nltk

from nltk import Text

from nltk.collocations import *

from Tools import tokenizer


class Collocations:

    def __init__(
        self,
        data,
        min_bigram_freq=None,
        min_trigram_freq=None,
    ):
        self.bigram_measures = nltk.collocations.BigramAssocMeasures()
        self.trigram_measures = nltk.collocations.TrigramAssocMeasures()
#         self.quadgram_measures = nltk.collocations.QuadgramAssocMeasures()
        self.min_bigram_freq = min_bigram_freq
        self.min_trigram_freq = min_trigram_freq
        if isinstance(data, basestring):
            self.corpus = Text([w.lower() for w in tokenizer(data)])
        elif isinstance(data, list):
            self.corpus = Text(data)


    def extract(self):
        self.bigram_finder = BigramCollocationFinder.from_words(self.corpus)
        self.trigram_finder = TrigramCollocationFinder.from_words(self.corpus)
#         self.quadgram_finder = QuadgramCollocationFinder.from_words(self.corpus)
        if self.min_bigram_freq:
            self.bigram_finder.apply_freq_filter(self.min_bigram_freq)
        if self.min_trigram_freq:
            self.trigram_finder.apply_freq_filter(self.min_trigram_freq)
#         if self.min_quadgram_freq:
#             self.quadgram_finder.apply_freq_filter(self.min_quadgram_freq)


    def __iter__(self, bigram_n=1000, trigram_n=1000):
        for coll in self.bigram_finder.nbest(self.bigram_measures.pmi, bigram_n) + \
                    self.trigram_finder.nbest(self.bigram_measures.pmi, trigram_n):
            yield coll
