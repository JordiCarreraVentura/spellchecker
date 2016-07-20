from __future__ import division
from Tools import to_csv


class Report:

    def __init__(self):
        self.runs = []
        self._rows = []
        self._tp = 0
        self._fp = 0
        self._tn = 0
        self._fn = 0
        self.tests = 0.0

    def lap(self, C):
        header = C.items()
        summary = (self.precision(), self.recall())
        print C
        print self
        print 
        self.runs.append((header, summary, self._rows))
        self._rows = []
        self._tp = 0
        self._fp = 0
        self._tn = 0
        self._fn = 0
        self.tests = 0.0
    
    def add(self):
        self.tests += 1
#         print self
    
    def precision(self):
        if not self._fp:
            return 1.0
        return round(self._tp / (self._tp + self._fp), 2)
    
    def recall(self):
        if not self._fn:
            return 1.0
        return round(self._tp / (self._tp + self._fn), 2)
    
    def __str__(self):
        return '<tp=%d  tn=%d  fp=%d  fn=%d  total=%d  prec=%.2f  rec=%.2f>' % (self._tp, self._tn, self._fp, self._fn, self.tests, self.precision(), self.recall())
    
    def fn(self, left, error, right, correct, category):
        self._rows.append(('fn', category, left, error, right, correct))
        self._fn += 1
    
    def tp(self, left, error, right, correct, category):
        self._rows.append(('tp', category, left, error, right, correct))
        self._tp += 1
        
    def tn(self, left, error, right, correct, category):
#         self._rows.append(('tn', category, left, error, right, correct))
        self._tn += 1
    
    def fp(self, left, error, right, correct, category):
        self._rows.append(('fp', category, left, error, right, correct))
        self._fp += 1
    
    def __call__(self, name):
        rows = []
        self.__save_summary('%s.log.csv' % name)
        self.__save_cases('%s.cases.csv' % name)

    def __save_summary(self, name):
        keys = ['run'] + list(zip(*self.runs[0][0])[0]) + ['precision', 'recall']
        rows = [keys]
        for i, (header, summary, _) in enumerate(self.runs):
            rows.append([i + 1] + list(zip(*header)[1]) + list(summary))
        to_csv(rows, name)
        
    def __save_cases(self, name):
        keys = ['run', 'outcome', 'error', 'left', 'error', 'right', 'correction']
        rows = [keys]
        for i, (_, _, cases) in enumerate(self.runs):
            for case in cases:
                rows.append([i + 1] + list(case))
        to_csv(rows, name)
