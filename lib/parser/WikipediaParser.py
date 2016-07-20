import csv
import bz2
import nltk
import json
import re
import sys
import time

from ..CategoryTree import CategoryTree

from ..Distribution import Distribution

from ..Tools import (
    decode,
    encode,
    to_csv,
    tokenizer
)

from ..TermIndex import TermIndex

from collections import (
    Counter,
    defaultdict as deft
)


TITLE = re.compile('<title>(.+)</title>')
REDIRECT = re.compile('<redirect title=\"(.+)\" />')
AMBIGUITY = re.compile('(.*)\(disambiguation\)')
CATEGORY = re.compile('\[\[Category:(.*?)\]\]')
BAR = re.compile('\|')
GREATER = re.compile('&gt;')
LESS = re.compile('&lt;')
SECTION = re.compile('={2,}[^a-z]{,3}(.*?)[^a-z]{,3}={2,}', re.IGNORECASE)
SQUARED_OPEN = re.compile('\[\[')
SQUARED_CLOSE = re.compile('\]\]')
CURLY_OPEN = re.compile('\{\{')
CURLY_CLOSE = re.compile('\}\}')
HTML = re.compile('<[^>]+>')


EXCLUDED = ['References', 'See also', 'External links']


class Streamer:

    def __init__(self):
        self.path = '/Users/jordi/Laboratorio/corpora/extracted/wikipedia/enwiki-20140707-pages-articles.xml.bz2'
        self.category_distribution = Counter()


    def vector(self, article):
#         data = self.__get_data(article['page'])
#         vector = self.__vector(data)
        vector = self.__bow(article['page'])
        return vector


    def articles(self):
        for block in self.__blocks():
            concept, ambiguity = self.__concept(block[0])

            if not concept[:2].isalpha():
                continue
            elif concept.startswith('List of'):
                continue
            
            redirect = self.__redirect(block)
            categories = self.__categories(block)
            text = ' '.join(block)

            if redirect:
                yield {
                    'variant': concept,
                    'concept': redirect,
                    'categories': categories,
                    'page': text
                }
            else:
                yield {
                    'variant': concept,
                    'concept': concept,
                    'categories': categories,
                    'page': text
                }


    def __categories(self, block):
        text = ' '.join(block)
        categories = []
        for match in CATEGORY.findall(text):
            _categories = [w.strip() for w in match.split('|')]
            categories += ['Category:%s' % c for c in _categories if c and c != '*']
        self.category_distribution.update(categories)
        return categories

    def __concept(self, part):
        match = TITLE.search(part)
        concept = match.group(1)

#         if not concept:
#             print '\n' * 3
#             print '\n'.join(['%s...' % part[:150] for part in block])
#             exit('FATAL: no concept!')

        ambiguity = AMBIGUITY.search(concept)
        if not ambiguity:
            return concept, False
        else:
            return ambiguity.group(1), True

    def __iter__(self):
        for block in self.__blocks():
            yield self.__block2article(block)
    
    def __block2article(self, block):
        return ' '.join(block)
    
    def __blocks(self):
        with bz2.BZ2File(self.path, mode='r') as rd:
            is_open = False
            block = []
            for line in rd:
                line = line.decode('utf-8').strip()
                if line == '<page>':
                    block = []
                    is_open = True
                    continue
                elif line == '</page>':
                    is_open = False
                    yield block
                if is_open:
                    block.append(line)
    
    def __redirect(self, block):
        for part in block:
            match = REDIRECT.match(part)
            if match:
                return match.group(1)
        return None
    
    def __get_data(self, block):
#         block = GREATER.sub('>', block)
#         block = LESS.sub('>', block)
#         block = HTML.sub('', block)
        sections, start, name, section = dict([]), 0, 'main', ''
        while True:
            match = SECTION.search(block)
            if not match:
                break
            section = block[:match.start()]
            if name not in EXCLUDED:
                sections[name] = self.__bow(section.strip())
            name = match.group(1)
            block = block[match.end():]
        if section:
            sections[name] = self.__bow(section)
        return sections
    
    def __bow(self, section):
#         section = self.__remove_header(section.strip())
#         return Counter(
#             [w.lower() for w in tokenizer(section)
#              if w.isalpha()]
#         )
        return [
            (w, f)
            for w, f in Counter([
                w.lower() for w in section.split()
                if w.isalpha()
            ]).most_common()
            if f > 3
        ]
    
    def __vector(self, data):
        vector = Counter()
        for section, freqs in data.items():
            for w, f in freqs.items():
                vector[w] += f
        return {w: f for w, f in vector.items() if f > 2}
    
#     def __remove_header(self, section):
#         return section


if __name__ == '__main__':
    
    streamer = Streamer()
    
    dist = Distribution('vector')
    category_index = TermIndex('category')
    variant_index = TermIndex('term')
    variants_by_concept = deft(list)
    categories_by_concept = deft(list)

    start = time.time()
    for i, article in enumerate(streamer.articles()):

#         if i <= 380000:
#             if not i % 1000:
#                 print '...', i
#             continue

        concept = article['concept']
        variant = article['variant']
        categories = article['categories']

        id_concept = variant_index(concept)
        id_variant = variant_index(variant)
        id_cats = [(c, category_index(c)) for c in categories]

        if not i % 200:
            print i, time.time() - start

        elif i >= 550000:				# temp
#         elif i >= 5000000:				# temp
            break						# temp
        
        variants_by_concept[id_concept].append(id_variant)
        if id_cats:
            categories_by_concept[id_concept] += zip(*id_cats)[1]
            
        if len(concept.split()) > 3:
            continue
        dist.update(id_concept, streamer.vector(article))

    #	save data to disk:
    category_index.to_csv()
    variant_index.to_csv()

    variant_data = sorted(
        [tuple([key] + sorted(items))
         for key, items in variants_by_concept.items()],
        key=lambda x: variant_index(key)
    )
    to_csv(variant_data, 'term.index.csv')
    
    category_data = sorted(
        [tuple([key] + sorted(items))
         for key, items in categories_by_concept.items()],
        key=lambda x: category_index(key)
    )
    to_csv(category_data, 'category.index.csv')
    
    dist.to_csv()
