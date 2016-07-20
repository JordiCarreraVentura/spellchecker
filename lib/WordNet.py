
import nltk

from nltk.corpus import wordnet as wn

from collections import defaultdict as deft


EXCLUDED = deft(bool)
for w in [
    'entity.n.01', 'abstraction.n.06', 'physical_entity.n.01',
    'psychological_feature.n.01', 'event.n.01', 'abstraction.n.06',
    'state.n.02', 'communication.n.02', 'act.n.02', 'whole.n.02',
    'content.n.05', 'message.n.02', 'group.n.01', 'quality.n.01',
    'attribute.n.02', 'relation.n.01', 'cognition.n.01', 'instrumentality.n.03',
    'object.n.01', 'location.n.01', 'fundamental_quantity.n.01', 'measure.n.02',
    'artifact.n.01', 'cognition.n.01', 'property.n.02', 'relation.n.01',
    'vertebrate.n.01', 'medium_of_exchange.n.01', 'legality.n.01', 'change.n.03',
    'fraction.n.03', 'process.n.06', 'action.n.01', 'definite_quantity.n.01',
    'chordate.n.01', 'representational_process.n.01', 'sidereal_day.n.01',
    'ideal.n.01', 'repeat.n.01', 'one.n.01', 'grammatical_category.n.01',
    'part.n.03', 'psychological_state.n.01', 'assignment.n.01',
    'out.n.01', 'kind.n.01', 'type.n.06'
]:
    EXCLUDED[w] = True



class WordNet:
    
    def __init__(self):
        return
    
    def __call__(self, w):
        synsets = {s.name(): [s] for s in wn.synsets(w) if s.pos() == 'n'}
        while True:
            some = False
            for name, s in synsets.items():
                hypernyms = s[-1].hypernyms()
                if not hypernyms:
                    continue
                else:
                    some = True
                    s.append(hypernyms[0])
#             print synsets
            if not some:
                break
        dump = []
        for name, ss in synsets.items():
            dump.append([s.name() for s in ss])
        return dump
    
#     def __lemmas(self, parents, hypernyms):
#         for h in hypernyms:
#             parents.update(h.lemma_names())
#         
#         
#     >>> def hypers(word):
# ...     for s in wordnet.synsets(word):
# ...         print s
# ...         for h in s.hypernyms():
# ...             print h
# ...             for _h in h.hypernyms():
# ...                 print '\t', _h
