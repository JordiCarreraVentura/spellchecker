import json

from collections import (
    Counter,
    defaultdict as deft
)

from copy import deepcopy as cp

# from cPickle import (
#     dump as to_pickle,
#     load as from_pickle
# )

from StringIO import StringIO

from TfIdfMatrix import TfIdfMatrix

from Tools import from_csv


class CategoryTree:
    
    def __init__(self, categories_by_concept, terms,
                 categories, tfidf, max_depth=5, min_df=20
    ):
        self.min_df = min_df
        self.path_categories_by_concept = categories_by_concept
        self.path_categories = categories
        self.path_terms = terms
        self.max_depth = max_depth
        self.observed_category = deft(bool)
        self.id_by_concept = dict([])
        self.concept_by_id = dict([])
        self.term_is_category = deft(bool)
        self.parents_by_category = dict([])
        self.parents_by_concept = deft(list)
        self.id_by_term = dict([])
        self.term_by_id = dict([])
        self.has_parents = deft(bool)
        self.tfidf = tfidf
        self.pulling = set([])
        self.vector_by_category = deft(Counter)
        self.contributors_by_category = deft(set)
        self.projected = Counter()

    def build(self):
        for i, c in enumerate(self.concept_by_id.values()):
            self(c)
            if not i % 100:
                t = float(len(self.concept_by_id.keys()))
                print i, int(t), round(i / t, 2)
#             if i >= 5000:
#                 break
    
    def dump(self):

        # Simulate a file with StringIO
        out = open('vector.dump.txt', 'wb')

        for i, (_id, projections) in enumerate(self.projected.items()):
        
            if not i % 100:
                print i, len(self.projected.keys())

            if not projections:
                continue

            features = [
                (self.tfidf.word_by_id[wid], round(weight, 4))
                for wid, weight in self.vector_by_category[_id].most_common()
                if round(weight, 4)
            ]
            record = (
                _id,
                self.concept_by_id[_id],
                features
            ) 
            out.write('%s\n' % str(record))

        out.close()


    def __call__(self, category):
        self.pulling = set([])
        return self.__pull(None, 0, category, dict([]))

    def __get_parents(self, _id):
        parents = []
        name = self.concept_by_id[_id]
        if (
            not self.observed_category[name] or
            not self.observed_category[_id] or
            not self.has_parents[_id]
        ):
            return []
        else:
            for i in self.parents_by_category[_id]:
                if not self.observed_category[i]:
                    continue
                _name = self.concept_by_id[i]
                parents.append(_name)
            return set(parents) - self.pulling


    def __pull(self, vector, depth, category, tree):
        _id = self.id_by_concept[category]
        if not self.pulling:
#             print
#             print
#             print category, _id
#             print [self.term_by_id[x] for x in self.contributors_by_category[_id]]
#             print self.vector_by_category[_id].most_common(20)
            vector = self.vector_by_category[_id]

        if not self.observed_category[category]:
            return dict([])

        parents = self.__get_parents(_id)
        if not parents or depth >= self.max_depth:
            tree[category] = dict([])
        else:
            subtree = dict([])
            self.pulling.update(parents)
            for parent in parents:
                subtree = self.__pull(vector, depth + 1, parent, subtree)
            tree[category] = subtree

        self.__project(vector, tree)

        return tree

    
    def __project(self, vector, tree):
        if not tree.keys():
            return
        else:
            for key, subtree in tree.items():
                _id = self.id_by_concept[key]
                self.projected[_id] += 1
                self.__add2vec(vector, _id)
                self.__project(vector, subtree)

    def __add2vec(self, vector, _id):
#         for w, weight in vector.items():
#             __id = self.tfidf.id_by_word[w]
        for __id, weight in vector.items():
            self.vector_by_category[_id][__id] += weight

    def load(self):
        self.__load_terms()
        self.__load_categories()
        self.__load_assignments()

    def __load_categories(self):
        for concept, _id in from_csv(self.path_categories):
            _id = int(_id)
            self.id_by_concept[concept] = _id
            self.concept_by_id[_id] = concept
            self.observed_category[_id] = True
            self.observed_category[concept] = True
#             print concept, _id, len(self.id_by_concept.keys())
#         exit()
    
    def __load_terms(self):
        for term, _id in from_csv(self.path_terms):
            _id = int(_id)
            self.term_by_id[_id] = term
            self.id_by_term[term] = _id
            if not term.startswith('Category:'):
                continue
            self.term_is_category[term] = True
            self.term_is_category[_id] = True

    def __load_assignments(self):
        for row in from_csv(self.path_categories_by_concept):
            ints = [int(field) for field in row]
            term_id = ints[0]
            term = self.term_by_id[term_id]
            if self.term_is_category[term_id] and \
            self.observed_category[term]:
                term = self.term_by_id[term_id]
                cat_id = self.id_by_concept[term]
                assignments = [i for i in ints[1:] if self.observed_category[i]]
                self.parents_by_category[cat_id] = assignments
                self.has_parents[cat_id] = True
            else:
                vector = self.tfidf.content(term_id)
                assignments = [i for i in ints[1:] if self.observed_category[i]]
                self.parents_by_concept[term_id] = assignments
                for a_id in assignments:
                    for w, weight in vector:
                        if self.tfidf.df[w] < self.min_df:
                            continue
                        #print term, term_id, self.concept_by_id[a_id], w, self.vector_by_category[a_id][w], '\t+%f' % weight
                        self.vector_by_category[a_id][w] += weight
                        self.contributors_by_category[a_id].update([term_id])



if __name__ == '__main__':
    
    import random
    from random import shuffle as randomize
    
    
    tfidf = TfIdfMatrix()
    tfidf.load_features('bkp.big.out/vector.term.csv')
    tfidf.load_distribution('bkp.big.out/vector.index.csv')
#     tfidf.load_features('vector.term.csv')
#     tfidf.load_distribution('vector.index.csv')

    ctree = CategoryTree(
        'bkp.big.out/category.index.csv',
        'bkp.big.out/term.csv',
        'bkp.big.out/category.csv',
#         'category.index.csv',
#         'term.csv',
#         'category.csv',
        tfidf,
        max_depth=1
    )
    ctree.load()
    ctree.build()
    ctree.dump()
    
