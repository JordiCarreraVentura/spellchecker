
from ..Tools import from_csv


class CSVSingleColumnParser:


    def __init__(self, column):
        self.column = column
        self.source = None
    

    def __call__(self, source):
        self.source = source
        return self
    
    
    def __iter__(self):
        for row in from_csv(self.source):
            yield row[self.column]
    
    
