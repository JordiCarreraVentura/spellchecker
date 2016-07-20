
import pattern

import re

from collections import (
    Counter,
    defaultdict as deft
)

from lib.WordNet import (
    EXCLUDED,
    WordNet
)

from Tools import ngrams

from pattern.en import (
    parse,
    parsetree
)


class PatternParser:
    
    def __init__(
        self,
        patterns=[
#             ('phrasal', ['(N.*|JJ)', 'N.*'], 'attribute'),
#             ('phrasal', ['(N.*|JJ)', '(N.*|JJ)', 'N.*'], 'attribute'),
#             ('phrasal', ['N.*', 'POS', 'N.*'], 'posessive'),
#             ('phrasal', ['(N.*|JJ)', '(N.*|JJ)', '(N.*|JJ)', 'N.*'], 'attribute'),
#             ('phrasal', ['(N.*|PRP)', 'CC', '(N.*|PRP)'], 'identity'),
#             ('sentential', ['(N.*|PRP)', 'V.*', '(N.*|PRP|JJ.*)'], 'event_relation'),
#             ('sentential', ['(N.*|PRP)', 'IN', '(N.*|PRP)'], 'entity_relation')
            ('sentential', ['(N.*)', '(VB[ZDGP]?)$', '(N.*|JJ.*)'], 'event_relation'),
#             ('sentential', ['N.*', '(IN|TO)', 'N.*'], 'entity_relation')
        ]
    ):
        self.patterns = deft(list)
        self.tags = Counter()
        for _type, rule, name in patterns:
            pattern = (tuple([re.compile(part) for part in rule]), name)
            self.patterns[_type].append(pattern)


    def __call__(self, text, relations=False, lemmata=False):
#         return parsetree(
#             text,
#             relations=relations,
#             lemmata=lemmata
#         )
        return parse(text, relations=True, lemmata=True)


    def triples(self, parsed):
        sents = parsed.split('\n')
        for s in sents:
            print s
        items = []
        for sent in sents:
#             print sent
            phrases = self.__phrases(sent)
            items += self.__relations(phrases)
        return items


    def __phrases(self, sent):
        tokens = [token.split('/') for token in sent.split()]
        phrases = []
        phrase = []
        last = ''
        while tokens:
            token = tokens.pop(0)
            try:
                form, pos, iob1, iob2, role, lemma = token
            except Exception:
                continue
            if iob2 != 'O':
                iob = iob2
            elif iob1 != 'O':
                iob = iob1
            else:
                iob = ''
            curr = iob.split('-')[-1]
#             if pos.endswith('PRP'):
#                 token = ('PERSON', pos, iob1, iob2, role, 'PERSON')
            if pos in ['JJR', 'JJS', 'RB'] or not lemma.isalpha():
                continue
            if (iob and iob.startswith('B')) or curr != last:
                phrases.append(phrase)
                phrase = [token]
            else:
                phrase.append(token)
            last = iob.split('-')[-1]
        if phrase:
            phrases.append(phrase)
        return phrases


    def __find_matches(self, patterns, poses):
        nn = sorted(set([len(parts) for parts, name in patterns]))
        matches = []
        for n in nn:
            grams = list(ngrams(poses, n))
            for i, gram in enumerate(grams):
                for parts, name in patterns:
                    hits = 0
                    if n != len(parts):
                        continue
                    for j, regex in enumerate(parts):
                        if regex.match(gram[j]):
                            hits += 1
                    if hits == len(parts):
#                         print n, i, gram, '\t', name, hits
                        matches.append((name, poses[i:i + len(gram)], i, i + len(gram)))
        return matches


    def __concatenate(self, sentential):
        cat = []
        for item in sentential:
            conn, pos, head = item
            if not conn:
                cat.append((pos, head))
            elif conn and (cat and cat[-1][0].startswith('N')):
                if conn != head:
                    cat.append(('IN', conn))
                cat.append((pos, head))
            else:
                cat.append((pos, head))
        return cat


    def __relations(self, phrases):
        relations = []
        patterns = self.patterns['phrasal']
        sentential = []
        wn = WordNet()
        for phrase in phrases:
            if not phrase:
                continue
            forms, poses, iob1s, iob2s, roles, lemmas = zip(*phrase)
            matches = self.__find_matches(patterns, poses)
            for name, pos, start, end in matches:
#                 relations.append((name, pos, lemmas[start:end]))
                relations.append((name, lemmas[start:end]))
            
            if iob1s[0].endswith('PP') or poses[0].endswith('TO'):
                sentential.append((lemmas[0], poses[-1], lemmas[-1]))
#             elif iob1s[0].endswith('VP'):
#                 sentential.append(('', poses[-1], lemmas[-1]))
            else:
                sentential.append(('', poses[-1], lemmas[-1]))
        
        if not sentential:
            return relations

        poses, lemmas = zip(*self.__concatenate(sentential))
        matches = self.__find_matches(self.patterns['sentential'], poses)
        for name, pos, start, end in matches:
#             relations.append((name, pos, lemmas[start:end]))
            words = lemmas[start:end]

            relations.append((name, lemmas[start:end]))

        return relations

