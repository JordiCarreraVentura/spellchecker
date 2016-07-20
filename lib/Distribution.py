from collections import (
    defaultdict as deft
)

from TermIndex import TermIndex

from Tools import to_csv as _to_csv


class Distribution:
    
    def __init__(self, name):
        self.name = name
        self.words = TermIndex('vector.term')
        self.vectors = dict([])
        self.seen = deft(bool)

    def update(self, id_concept, vector):

        if len(vector) < 20:
            return

        if not self.seen[id_concept]:
            self.vectors[id_concept] = deft(bool)
            self.seen[id_concept] = True
        _vector = self.vectors[id_concept]
        
        for word, freq in vector:
            _id = self.words(word)
            _vector[_id] += freq


    def to_csv(self):
        self.words.to_csv()
        rows = []
        for _id, vector in self.vectors.items():
            row = [_id] + ['%d=%d' % (i, f) for i, f in vector.items()]
            if row[1:]:
                rows.append(row)
        _to_csv(rows, 'vector.index.csv')
