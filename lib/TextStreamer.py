from tqdm import tqdm

# from lib.Tools import (
from Tools import (
    decode as d,           # Auxiliary method to decode UTF-8 (when reading from a file)
    encode as e            # Auxiliary method to encode UTF-8 (when writing to a file or stdout)
)

class TextStreamer:
    
    def __init__(self, source, parser=None):
        self.source = source
        self.n = 50000
        self.c = 0
        if parser:
            self.parser = parser(self.source)
        else:
            self.parser = None

    def __iter__(self):
        if not self.parser:
            with open(self.source, 'rb') as rd:
                for line in rd:
                    self.c += 1
                    if not line.strip():
                        continue
                    yield d(line)
                    if self.c >= self.n:
                        break
        else:
            for parsed in self.parser:
                yield d(parsed)



if __name__ == '__main__':

    path = '/Users/jordi/Laboratorio/corpora/raw/linguistlist/txt/2015-May.txt'
# #     path = '/Users/jordi/Laboratorio/corpora/raw/Kaggle Billion word imputation corpus/train_v2.txt'

#     strr = TextStreamer(path)
#     for unit in tqdm(strr):
#         print '<open>%s<close>' % unit
#     exit()
#             
    strr = TextStreamer(path, parser=Parser)
    for unit in tqdm(strr):
        continue
#         print '<open>%s<close>' % unit
