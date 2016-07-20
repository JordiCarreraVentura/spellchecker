
from Tools import (
    splitter,
    tokenizer
)


class NaiveTokenizer:
    
    def __init__(self, streamer, n=None, to_lower=False):
        self.streamer = streamer
        self.to_lower = to_lower
        self.i = 0
        self.iter = -1
        self.n = n

    def restart(self):
        self.i = 0
        self.iter += 1
    
    def progress(self):
        self.i += 1
        if self.i and not self.i % 2000:
            print '<iter=%d records=%d>' % (self.iter, self.i)

    def __iter__(self):
        self.restart()
        for record in self.streamer:
            self.progress()
            if self.n and self.i == self.n:
                break				
            try:
                for sentence in splitter(record):
                    if not self.to_lower:
                        yield tokenizer(sentence)
                    else:
                        yield [w.lower() for w in tokenizer(sentence)]
            except Exception:
                continue
