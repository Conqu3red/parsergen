# Code @generated by parsergen; do not edit!
from parsergen.parser_utils import GeneratedParser, TokenStream, Node, Filler
from parsergen.parser_utils import memoize, memoize_left_rec
from functools import reduce

class CustomParser(GeneratedParser):
    @memoize
    def start(self):
        pos = self.mark()
        parts = [
            self.expr(),
            self.expect('EOF'),
        ]
        if self.match(parts):
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def expr(self):
        pos = self.mark()
        parts = [
            self.expr(),
            self.expect('ADD'),
            self.term(),
        ]
        if self.match(parts):
            left = parts[0]
            right = parts[2]
            return left + right
        self.goto(pos)
        
        parts = [
            self.expr(),
            self.expect('SUB'),
            self.term(),
        ]
        if self.match(parts):
            left = parts[0]
            right = parts[2]
            return left - right
        self.goto(pos)
        
        parts = [
            self.term(),
        ]
        if self.match(parts):
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def term(self):
        pos = self.mark()
        parts = [
            self.term(),
            self.expect('MUL'),
            self.factor(),
        ]
        if self.match(parts):
            left = parts[0]
            right = parts[2]
            return left * right
        self.goto(pos)
        
        parts = [
            self.term(),
            self.expect('DIV'),
            self.factor(),
        ]
        if self.match(parts):
            left = parts[0]
            right = parts[2]
            return left / right
        self.goto(pos)
        
        parts = [
            self.factor(),
        ]
        if self.match(parts):
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def factor(self):
        pos = self.mark()
        parts = [
            self.item(),
            self.expect('POW'),
            self.factor(),
        ]
        if self.match(parts):
            left = parts[0]
            right = parts[2]
            return left ** right
        self.goto(pos)
        
        parts = [
            self.item(),
        ]
        if self.match(parts):
            e = parts[0]
            return e
        self.goto(pos)
        
        return None
        
    @memoize_left_rec
    def item(self):
        pos = self.mark()
        parts = [
            self.expect('INT'),
        ]
        if self.match(parts):
            n = parts[0]
            return int(n.value)
        self.goto(pos)
        
        parts = [
            self.expect('LPAREN'),
            self.expr(),
            self.expect('RPAREN'),
        ]
        if self.match(parts):
            e = parts[1]
            return e
        self.goto(pos)
        
        return None
        
