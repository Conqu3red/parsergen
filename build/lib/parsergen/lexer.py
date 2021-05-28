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
    def __init__(self):
        self.token_list: List[Token] = []

        self.init()
    
    def init(self):
        self.lineno = 1
        self.column = 0
        self.curPos = 0
        self.token_list = []
    
    def Token(self, value, tokenType):
        token = Token(
            value, tokenType,
            lineno=self.lineno, column=self.column
        )
        return token
    
    def step_source(self, to_index):
        self.column += to_index
        self.source = self.source[to_index:]
    
    def getToken(self):
        if self.source[0] == "\n":
            self.lineno += 1
            self.column = 0
            #self.step_source(1)
        
        for token_name, regex in self.tokens.items():
            r = re.match(regex, self.source)
            if r:
                self.step_source(r.span()[1])
                return self.Token(r.group(), token_name)
        raise Exception(f"Found Unexpected character '{self.source[0]}' while tokenizing!")
        
        

    def lexString(self, source):
        self.init()
        self.source = source
        self.lines = source.split("\n")
        while len(self.source) > 0:
            #print(repr(self.source))
            while self.source[0] in self.ignore:
                self.step_source(1)
            token = self.getToken()
            self.token_list.append(token)
        return LexerResult(self.token_list, self.lines)


del Lexer.tokens, Lexer.ignore