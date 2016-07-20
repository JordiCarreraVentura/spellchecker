
from Tools import (
    remove_nonwords,
    tokenizer
)


class FeatureEngine:
    
    def __init__(
        self,
        bow=False
    ):
        self.bow = bow
    
    def __call__(self, text):
        if self.bow:
            return self.__bow(text)
        else:
            return text
    
    def __bow(self, text):
        tokens = [w.lower() for w in tokenizer(text)]
        words = remove_nonwords(tokens)
        return words
