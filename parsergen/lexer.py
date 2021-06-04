"""Creates the Token class and regex matching Lexer"""
from dataclasses import dataclass
from typing import *
import re
from .utils import *
import itertools

class Token(object):
    def __init__(self, type, value, lineno=0, column=0):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column
    
    def __str__(self):
        return f"<Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno}, column={self.column})>"
    
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

def token(*rules):
    def inner(func):
        func._rules = list(rules)
        return func
    return inner

class Rule:
    def __init__(self, match: List[str], modifier=None) -> None:
        self.match = match
        self.modifier = modifier

class LexerMetaDict(dict):
    """Special dictionary to allow definition of tokens in the Lexer"""
    def __setitem__(self, k, v) -> None:
        if hasattr(v, "_rules") and k != "_rules": # modifer on token
            target = "_rules"
            if k.startswith("ignore_"):
                target = "_ignores"
            rules = v._rules
            if k not in self[target]:
                self[target][k] = Rule(match=rules, modifier=v)
            else:
                self[target][k].match += rules
                self[target][k].modifier = v
            return
        elif re.match(r"[A-Z0-9_]+$", k) or re.match(r"ignore_.+", k):
            target = "_rules"
            if k.startswith("ignore_"):
                target = "_ignores"
            
            if isinstance(v, (str, Sequence)):
                rules = [v] if isinstance(v, str) else list(v)
                if k not in self[target]:
                    self[target][k] = Rule(match=rules)
                else:
                    self[target][k].match += rules
            else:
                if k not in self[target]:
                    self[target][k] = Rule(match=[], modifier=v)
                else:
                    self[target][k].modifier = v
        
        return super().__setitem__(k, v)

class LexerMeta(RequiredAttributes("ignore")):
    @classmethod
    def __prepare__(meta, name, bases):
        d = LexerMetaDict()
        d["token"] = token
        d["_rules"] = {}
        d["_ignores"] = {}
        return d
    
    @property
    def tokens(cls):
        return tuple(cls._rules.keys())

# need to modify lexer to accept the new Rule objects
# modify documentation
# add other support?
class Lexer(metaclass=LexerMeta):
    ignore = None
    _rules: Dict[str, Rule]
    _ignores: Dict[str, Rule]
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
    
    def Token(self, tokenType, value):
        token = Token(
            tokenType, value,
            lineno=self.lineno, column=self.column
        )
        return token
    
    def step_source(self, to_index):
        self.column += to_index
        self.current_line += self.source[:to_index]
        self.source = self.source[to_index:]
    
    def getToken(self) -> Token:
        for token_name, rule in itertools.chain(self._rules.items(), self._ignores.items()):
            for regex in rule.match:
                r = re.match(regex, self.source)
                if r:
                    self.step_source(r.span()[1])
                    rv = self.Token(token_name, r.group())
                    if rule.modifier:
                        rv = rule.modifier(self, rv)
                    return rv if not token_name.startswith("ignore_") else None
        raise Exception(f"Found Unexpected character '{self.source[0]}' while tokenizing!")
        

    def lex_string(self, source: str) -> LexerResult:
        self.init()
        self.source = source
        self.lines = []
        
        while len(self.source) > 0:
            while len(self.source) > 0 and self.source[0] in self.ignore:
                self.step_source(1)
            #for token_name, rule in self._ignores.items():
            #    for regex in rule.match:
            #        r = re.match(regex, self.source)
            #        if r:
            #            self.step_source(r.span()[1])
            #            rv = self.Token(token_name, r.group())
            #            if rule.modifier:
            #                rv = rule.modifier(self, rv)
            if len(self.source) == 0:
                break
            token = self.getToken()
            if token:
                self.token_list.append(token)
        
        self.lines.append(self.current_line) # final line
        return LexerResult(self.token_list, self.lines)


del Lexer.ignore

class TokenStream:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
    
    def mark(self):
        return self.pos
    
    def goto(self, pos):
        self.pos = pos
    
    def get_token(self):
        tok = self.peek_token()
        self.pos += 1
        return tok
    
    def peek_token(self):
        if self.pos >= len(self.tokens):
            return Token("EOF", "<EOF>")
        return self.tokens[self.pos]