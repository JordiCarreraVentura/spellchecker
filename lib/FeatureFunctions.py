
import re

LETTERS = re.compile('[a-z]+')


def is_punct(w):
    if LETTERS.search(w):
        return 'punct_0'
    else:
        return 'punct_1'

def 
