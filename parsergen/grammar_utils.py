from typing import *
from .lexer import *

class AST(object):
    pass


class Pointer(AST):
    def __init__(self, target: str) -> None:
        self.target = target
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(target={self.target!r})"


class StatementPointer(Pointer):
    pass


class TokenPointer(Pointer):
    pass


class Expr(AST):
    pass


class ExprList(AST):
    def __init__(self, exprs) -> None:
        self.exprs = exprs
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(exprs={self.exprs!r})"


class Quantifier(Expr):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(expr={self.expr!r})"


class ZeroOrMore(Quantifier):
    pass


class OneOrMore(Quantifier):
    pass


class ZeroOrOne(Quantifier):
    pass


class OrOp(Expr):
    def __init__(self, exprs: List[Expr]) -> None:
        self.exprs = exprs
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(exprs={self.exprs!r})"


class NamedItem(Expr):
    def __init__(self, name: str, expr: Expr) -> None:
        self.name = name
        self.expr = expr

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name!r}, expr={self.expr!r})"


class Statement(object):
    def __init__(self, name: str, grammar: List[Expr], action=None) -> None:
        self.name = name
        self.grammar = grammar
        self.action = action
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name!r}, grammar={self.grammar!r})"




class GrammarLexer(Lexer):
    ID =        r"[a-z0-9_]+"
    TOKEN =     r"[A-Z0-9_]+"
    COLON =     r"\:"
    OR =        r"\|"
    STAR =      r"\*"
    PLUS =      r"\+"
    QMARK =     r"\?"
    LPAREN =    r"\("
    RPAREN =    r"\)"
    TERMINATE = r";"
    EQ        = r"="
    @token(r"\{([\s\S]+?)\}\s*;\s*(\n|$)")
    def ACTION(self, t):
        self.source = ";\n" + self.source
        t.value = re.match(r"\{([\s\S]+?)\}\s*;\s*(\n|$)", t.value).group(1).strip()
        return t
    
    @token(r"\n")
    def NEWLINE(self, t):
        self.lineno += 1
        self.column = 0
    
    ignore = " \t"
