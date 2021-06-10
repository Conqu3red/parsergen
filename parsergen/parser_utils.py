from typing import Optional
from .lexer import TokenStream
from functools import wraps

class Filler:
    def __repr__(self) -> str:
        return "Filler()"

class Node:
    def __init__(self, type, children: list) -> None:
        self.type = type
        self.children = children
    
    def __repr__(self) -> str:
        return f"Node({self.type!r}, {self.children!r})"

def memoize(func):
    @wraps(func)
    def memoize_wrapper(self, *args):
        pos = self.mark()
        memo = self.memos
        key = (pos, func, args)
        if key in memo:
            res, endpos = memo[key]
            self.goto(endpos)
        else:
            res = func(self, *args)
            endpos = self.mark()
            memo[key] = res, endpos
        return res
    return memoize_wrapper


def memoize_left_rec(func):
    # https://github.com/PhilippeSigaud/Pegged/wiki/Left-Recursion
    @wraps(func)
    def memoize_left_rec_wrapper(self, *args):
        pos = self.mark()
        memo = self.memos
        key = (pos, func, args)
        if key in memo:
            res, endpos = memo[key]
            self.goto(endpos)
        else:
            # Prime the cache with a failure.
            memo[key] = lastres, lastpos = None, pos
            # Loop until no longer parse is obtained.
            while True:
                self.goto(pos)
                res = func(self, *args)
                endpos = self.mark()
                if endpos <= lastpos:
                    break
                memo[key] = lastres, lastpos = res, endpos
            res = lastres
            self.goto(lastpos)
        return res
    return memoize_left_rec_wrapper


class ParseError(Exception):
    def __init__(self, msg, lineno, column, lineText=""):
        self.msg = msg
        self.lineno = lineno
        self.column = column
        self.lineText = lineText
    
    def __str__(self):
        ret = f"\n  Line {self.lineno}:\n"
        if self.lineText:
            ret += f"  {self.lineText}\n  {' '*(self.column-1)}^\n"
        return ret + f"{self.msg}"


class GeneratedParser:
    _or = lambda _, a, b: a or b

    def __init__(self, token_stream: TokenStream) -> None:
        self.memos = {}
        self.token_stream = token_stream
        self.error_pos = -1

    def fail(self):
        pos = self.mark()
        if pos > self.error_pos:
            self.error_pos = pos
    
    def error(self) -> Optional[ParseError]:
        if self.error_pos == -1:
            return None
        tok = self.fetch(self.error_pos)
        return ParseError(
            f"Unexpected token {tok.error_format()}", 
            *tok.pos,
            lineText=self.token_stream.lines[tok.lineno-1] if tok.lineno-1 < len(self.token_stream.lines) else ""
        )
    
    def mark(self):
        return self.token_stream.mark()
    
    def goto(self, pos):
        self.token_stream.goto(pos)
    
    @memoize
    def expect(self, type):
        tok = self.peek_token()
        if tok.type == type:
            self.token_stream.pos += 1
            return tok
        return None
    
    def peek_token(self):
        return self.token_stream.peek_token()
    
    def fetch(self, pos):
        return self.token_stream.fetch(pos)
    
    def match(self, part):
        if isinstance(part, list):
            for p in part:
                if isinstance(p, list):
                    if not self.match(p):
                        return False
                elif p is None:
                    return False
        elif part is None: # TODO: check if this causes issues
            return False
        return True