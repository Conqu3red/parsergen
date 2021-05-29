"""Creates the Token class and regex matching Lexer"""
from dataclasses import dataclass
from typing import *
import re
from .utils import *

class Token(object):
    def __init__(self, value, _type, lineno=0, column=0):
        self.value = value
        self.type = _type
        self.lineno = lineno
        self.column = column
    
    def __str__(self):
        return f"<Token(value={self.value!r}, type={self.type!r}, position={self.lineno}:{self.column})>"
    
    def __repr__(self):
        return self.__str__()
    
    def error_format(self):
        return f"'{self.value}' ({self.type})"
    
    @property
    def pos(self):
        return self.lineno, self.column

@dataclass
class LexerResult:
    tokens: List[Token]
    lines: List[str]

class Lexer(metaclass=RequiredAttributes("tokens", "ignore")):
    tokens = ignore = None
    _lineno: int
    
    def __init__(self):
        self.token_list: List[Token] = []
        self.init()
    
    def init(self):
        self.current_line = ""
        self._lineno = 1
        self.lineno = 1
        self.column = 0
        self.token_list = []
    
    @property
    def lineno(self) -> int:
        return self._lineno
    
    @lineno.setter
    def lineno(self, value):
        if self._lineno < value:
            self.lines.append(self.current_line)
            self.current_line = ""
        self._lineno = value
    
    def Token(self, value, tokenType):
        token = Token(
            value, tokenType,
            lineno=self.lineno, column=self.column
        )
        return token
    
    def step_source(self, to_index):
        self.column += to_index
        self.current_line += self.source[:to_index]
        self.source = self.source[to_index:]
    
    def getToken(self) -> Token:
        for token_name, regex in self.tokens.items():
            modifier = None
            if isinstance(regex, tuple):
                regex, modifier = regex
            r = re.match(regex, self.source)
            if r:
                self.step_source(r.span()[1])
                rv = self.Token(r.group(), token_name)
                if modifier:
                    rv.value = modifier(self, rv.value)
                return rv
        raise Exception(f"Found Unexpected character '{self.source[0]}' while tokenizing!")
        

    def lexString(self, source: str) -> LexerResult:
        self.init()
        self.source = source
        self.lines = []
        
        while len(self.source) > 0:
            while len(self.source) > 0 and self.source[0] in self.ignore:
                self.step_source(1)
            if len(self.source) == 0:
                break
            token = self.getToken()
            self.token_list.append(token)
        
        self.lines.append(self.current_line) # final line
        return LexerResult(self.token_list, self.lines)


del Lexer.tokens, Lexer.ignore