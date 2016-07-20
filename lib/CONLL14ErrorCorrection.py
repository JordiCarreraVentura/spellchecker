
import nltk

from nltk import (
    sent_tokenize as splitter,
    wordpunct_tokenize as tokenize
)

from Tools import (
    strip_punct
)

from copy import deepcopy as cp

from collections import defaultdict as deft

import re

CONLL_PATH = 'data/official-2014.%s.sgml'

DOC = re.compile('<DOC.*?>(.+?)</DOC>', re.DOTALL)
TEXT = re.compile('<TEXT.*?>(.+?)</TEXT>', re.DOTALL)
ANNOTATION = re.compile('<ANNOTATION.*?>(.+?)</ANNOTATION>', re.DOTALL)
MISTAKE = re.compile('<MISTAKE (.*?)>(.+?)</MISTAKE>', re.DOTALL)
TYPE = re.compile('<TYPE.*?>(.+?)</TYPE>', re.DOTALL)
CORRECTION = re.compile('<CORRECTION.*?>(.*?)</CORRECTION>', re.DOTALL)
TYPE = re.compile('<TYPE.*?>(.*?)</TYPE>', re.DOTALL)
META = re.compile('start_par=\"(.*?)\" start_off=\"(.*?)\" end_par=\"(.*?)\" end_off=\"(.*?)\"')
PARAGRAPH = re.compile('<(TITLE|P)>(.+?)</(TITLE|P)>', re.DOTALL)


class CONLL14ErrorCorrection:
    
    def __init__(self, annotator='0'):
        self.source = CONLL_PATH % annotator
        self.txt = self.__txt()
        self.space = cp(self.txt)
    
    def __txt(self):
        lines = []
        with open(self.source, 'rb') as rd:
            for line in rd:
                lines.append(line.decode('utf-8').strip())
        return '\n'.join(lines)
    
    def __iter__(self):
        for doc in self.space.split('</DOC>'):
            for item in self.__data(doc):
                yield item
    
    def __data(self, doc):
        paragraphs = [par[1].strip() for par in PARAGRAPH.findall(doc)]
        mistakes = MISTAKE.findall(doc)

        errors = []
        for problem, entry in mistakes:
            correction = CORRECTION.search(entry).group(1)
            _type = TYPE.search(entry).group(1)
            meta = META.search(problem)
            par_start, char_start, par_end, char_end = int(meta.group(1)), \
                                                       int(meta.group(2)), \
                                                       int(meta.group(3)), \
                                                       int(meta.group(4))
            if par_end != par_start:
                continue
            mistake = (
                par_start,
                char_start,
                char_end,
                correction,
                _type
            )
            errors.append(mistake)

        errors_by_par = deft(list)
        for mistake in errors:
            errors_by_par[mistake[0]].append(mistake)

        items = []
        for p, errors in errors_by_par.items():
            par = paragraphs[p]
            space = cp(par)
            contexts = []
            for _, start, end, corr, category in errors:
                left = ' '.join(par[:start].split()[-10:])
                right = ' '.join(par[end:].split()[:10])
                err = par[start:end]
                contexts.append((left, strip_punct(err.lower()), right,
                                 strip_punct(corr.lower()), category))
                space = space[:start] + \
                        '#' * len(err) + \
                        space[end:]

#         print len(contexts), contexts
            focus = 0
            for w in space.split():
                if w.startswith('#'):
                    items.append((contexts[focus], 'tp'))
                    focus += 1
                else:
                    items.append(
                        ((None, None, None, strip_punct(w.lower()), None), 'tn')
                    )

        return items

#         print space
#         print items
            
#             par, start, end, corr, _type
#             parag = paragraphs[par]
#             prefix = parag[:start]
#             error = parag[start:end]
#             suffix = parag[end:]
#             correction = corr
#             yield (prefix, error, suffix, correction, _type)
            



if __name__ == '__main__':
    c = CONLL14ErrorCorrection()
    for left, error, right, correction, category in c:
        print '%s | %s | %s | %s | %s' % (left, error, right, correction, category)
