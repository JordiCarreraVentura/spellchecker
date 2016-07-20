
import re

class LinguistListParser:
    
    def __init__(self, path):
        self.source = path
        self.separator = 'From linguist at listserv.linguistlist.org'
        self.subject = re.compile('(Subject:.*)\n')
    
    def __iter__(self):
        block = []
        with open(self.source, 'rb') as rd:
            for line in rd:
                if block and line.startswith(self.separator):
                    yield ''.join(block)
                    block = [line]
                else:
                    block.append(line)
            if block:
                yield ''.join(block)
    
    def subjects(self):
        block = []
        with open(self.source, 'rb') as rd:
            for line in rd:
                if block and line.startswith(self.separator):
                    yield self.subject.search(''.join(block)).group(1)
                    block = [line]
                else:
                    block.append(line)
            if block:
                yield self.subject.search(''.join(block)).group(1)
                
    def longest_lines(self):
        block = []
        with open(self.source, 'rb') as rd:
            for line in rd:
                if block and line.startswith(self.separator):
                    yield self.__longest_line(block)
                    block = [line]
                else:
                    block.append(line)
            if block:
                yield self.__longest_line(block)
    
    def __longest_line(self, block):
        return sorted(
            [(len(l), l.strip()) for l in block]
        )[-1][1]
