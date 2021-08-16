from typing import *
from .lexer import *
import codecs

class AST(object):
    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v!r}" for k,v in vars(self).items())
        return f"{self.__class__.__qualname__}({params})"

class Terminator(AST):
    pass

class Pointer(Terminator):
    def __init__(self, target: str) -> None:
        self.target = target
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(target={self.target!r})"


class StatementPointer(Pointer):
    pass


class TokenPointer(Pointer):
    pass

class ConstantString(Terminator):
    def __init__(self, value: str) -> None:
        self.value = value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(value={self.value!r})"


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


class Predicate(Expr):
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(expr={self.expr!r})"

class AndPredicate(Predicate):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr


class NotPredicate(Predicate):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr

class Section(AST):
    pass

class Statement(Section):
    def __init__(self, name: str, grammar: List[Expr], action=None) -> None:
        self.name = name
        self.grammar = grammar
        self.action = action
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name!r}, grammar={self.grammar!r})"

class ConfigurationCall(Section):
    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name!r}, value={self.value!r})"

class ParserDefinition(AST):
    def __init__(self, sections: List[Section]) -> None:
        self.sections = sections
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(sections={self.sections!r})"


class GrammarLexer(Lexer):
    ID        = r"[a-z0-9_]+"
    TOKEN     = r"[A-Z0-9_]+"
    COLON     = r"\:"
    OR        = r"\|"
    STAR      = r"\*"
    PLUS      = r"\+"
    QMARK     = r"\?"
    LPAREN    = r"\("
    RPAREN    = r"\)"
    TERMINATE = r";"
    EQ        = r"="
    NOT       = r"!"
    AND       = r"&"
    AT        = r"@"
    
    @token(r"\{([\s\S]+?)\}\s*;\s*(\n|$)")
    def ACTION(self, t):
        self.source = ";\n" + self.source
        t.value = re.match(r"\{([\s\S]+?)\}\s*;\s*(\n|$)", t.value).group(1).strip()
        return t
    
    @token(r"(')")
    def STRING(self, t):
        end = t.value
        escape = False
        result = ""
        while True:
            if len(self.source) > 0:
                cur_char = self.source[0]
                self.step_source(1)
                if not escape and cur_char == "\\":
                    result += cur_char
                    if len(self.source) == 0:
                        continue
                    cur_char = self.source[0]
                    self.step_source(1)
                    escape = True
                if cur_char == end and not escape:
                    t.value = codecs.getdecoder("unicode_escape")(result)[0]
                    return t
                result += cur_char
                escape = False
            else:
                raise Exception("No end of string")
    
    @token(r"\n")
    def NEWLINE(self, t):
        self.lineno += 1
        self.column = 0
    
    ignore = " \t"
