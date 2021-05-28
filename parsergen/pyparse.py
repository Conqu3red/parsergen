"""Parses grammar expressions and performs pattern matching

Tokens:
    ID      :   [a-z_]+
    TOKEN   :   [A-Z_]+


Grammar:

statement  :  ID COLON (expr)*
expr       :  item
expr       :  expr OR expr
expr       :  expr STAR
expr       :  expr PLUS
expr       :  expr QMARK
expr       :  LPAREN expr RPAREN

item       :  ID | TOKEN
"""
from .lexer import *
from .utils import *
from typing import *
import inspect
import functools


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


class Statement(object):
    def __init__(self, name: str, grammar: List[Expr]) -> None:
        self.name = name
        self.grammar = grammar
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name!r}, grammar={self.grammar!r})"


class GrammarLexer(Lexer):
    tokens = {
        "ID":      r"[a-z_]+",
        "TOKEN":   r"[A-Z_]+",
        "COLON":   r":",
        "OR":      r"\|",
        "STAR":    r"\*",
        "PLUS":    r"\+",
        "QMARK":   r"\?",
        "LPAREN":  r"\(",
        "RPAREN":  r"\)",
        "NEWLINE": r"\n"
    }
    ignore = " \t"


class GrammarParser(object):
    def __init__(self) -> None:
        pass

    def eat(self, token_name: str):
        if self.current_token.type == token_name:
            self.tokens.pop(0)
        else:
            raise Exception(f"Found Token '{self.current_token.type}' but expected Token '{token_name}'")

    def eof(self):
        return Token("<EOF>", "EOF")

    @property
    def current_token(self):
        if len(self.tokens) > 0:
            return self.tokens[0]
        return self.eof()

    def statement(self) -> Statement:
        "ID COLON (expr)*"
        token = self.current_token
        self.eat("ID")
        name = token.value
        expr = []
        self.eat("COLON")
        while len(self.tokens) > 0 and self.current_token.type != "NEWLINE":
            expr.append(self.expr())
        
        return Statement(name, expr)
    
    def expr_list(self):
        "expr*"
        exprs = []
        while len(self.tokens) > 0 and self.current_token.type != "RPAREN":
            exprs.append(self.expr())
        return ExprList(exprs)
    
    def expr(self):
        """
        expr  :  item
              |  or_op
              |  expr STAR
              |  expr PLUS
        """
        node = self.item()

        if self.current_token.type == "OR":
            node = self.or_op(node)
        elif self.current_token.type == "STAR":
            self.eat("STAR")
            node = ZeroOrMore(node)
        elif self.current_token.type == "PLUS":
            self.eat("PLUS")
            node = OneOrMore(node)
        elif self.current_token.type == "QMARK":
            self.eat("QMARK")
            node = ZeroOrOne(node)
        return node
    
    def or_op(self, node) -> OrOp:
        "or_op  :  expr (OR expr)*"
        exprs = [node]
        while self.current_token.type == "OR":
            self.eat("OR")
            exprs.append(self.expr())
        
        return OrOp(exprs)


    def item(self):
        """
        item  :  ID | TOKEN
              |  LPAREN expr RPAREN
        """
        t = self.current_token
        #print(f"item - {t}")
        if t.type == "ID":
            self.eat(t.type)
            return StatementPointer(t.value)
        elif t.type == "TOKEN":
            self.eat(t.type)
            return TokenPointer(t.value)
        elif t.type == "LPAREN":
            self.eat("LPAREN")
            rv = self.expr_list()
            self.eat("RPAREN")
            return rv



    def parse(self, tokens: List[Token]):
        self.tokens = tokens

        return self.statement() # curently only supports a single statement


class StatementAndTarget(NamedTuple):
    statement: Statement
    function: Any


def get_class_that_defined_method(meth):
    "https://stackoverflow.com/a/25959545"
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects


def grammar(statement):
    class _grammar_creator:
        def __init__(self, fn):
            self.fn = fn

        def __set_name__(self, owner: Parser, name):
            l = GrammarLexer()
            tokens = l.lexString(statement).tokens
            r = GrammarParser().parse(tokens)

            if getattr(owner, "_grammar", None) is None:
                owner._grammar = {}

            if r.name not in owner._grammar:
                owner._grammar[r.name] = [StatementAndTarget(statement=r, function=self.fn)]
            else:
                owner._grammar[r.name].append(StatementAndTarget(statement=r, function=self.fn))

            setattr(owner, name, self.fn)
    
    return _grammar_creator


class Parser(metaclass=RequiredAttributes("tokens")):
    _grammar: Dict[str, List[StatementAndTarget]]
    tokens = None
    
    @property
    def current_token(self) -> Token:
        try:
            return self.tokens[self.index]
        except IndexError:
            return Token("<EOF>", "__EOF__")


    def pattern_match(self, starting_point=None) -> List[Any]:
        self.indent = 0
        if starting_point is not None:
            matched, result = self.process_StatementAndTargetList(self._grammar[starting_point])
            if matched:
                return result
            return
        
        for identifier in self._grammar:
            matched, result = self.process_StatementAndTargetList(self._grammar[identifier])
            if matched:
                return result

    def process(self, ast: AST) -> Tuple[bool, Any]:
        target = f"process_{ast.__class__.__qualname__}"
        #print(self.indent * "|" + target, " ", ast)
        self.indent += 1
        r = getattr(self, target)(ast)
        self.indent += -1
        #print(self.indent * "|" + target, "RET ", ast, r)
        return r
    
    def process_StatementAndTargetList(self, statements: List[StatementAndTarget]) -> Tuple[bool, Any]:
        for statement, func in statements:
            i = self.index
            matched, result = self.process(statement)
            if matched:
                return True, func(self, result)
            self.index = i
        
        return False, None
    
    def process_Statement(self, statement: Statement) -> Tuple[bool, List[Any]]:
        result = []
        for part in statement.grammar:
            matched, r = self.process(part)
            result.append(r)
            if not matched:
                break
        else:
            return True, result
        return False, []
    
    def process_ExprList(self, exprList: ExprList) -> Tuple[bool, List[Any]]:
        result = []
        i = self.index
        for expr in exprList.exprs:
            matched, r = self.process(expr)
            result.append(r)
            if not matched:
                break
        else:
            return True, result
        self.index = i
        return False, []

    def process_TokenPointer(self, pointer: TokenPointer) -> Tuple[bool, Any]:
        if self.current_token.type == pointer.target:
            rv = True, self.current_token.value
            self.index += 1
        else:
            return False, None
        return rv
    
    def process_StatementPointer(self, pointer: StatementPointer) -> Tuple[bool, Any]:
        return self.process_StatementAndTargetList(self._grammar[pointer.target])
    
    def process_ZeroOrMore(self, quantifier: ZeroOrMore) -> Tuple[bool, Any]:
        result = []
        match = True
        while match:
            match, r = self.process(quantifier.expr)
            if match:
                result.append(r)
            else:
                break
        return True, result
    
    def process_OneOrMore(self, quantifier: OneOrMore) -> Tuple[bool, Any]:
        result = []
        match = True
        while match:
            match, r = self.process(quantifier.expr)
            if match:
                result.append(r)
        if len(result) == 0:
            return False, result
        return True, result
    
    def process_ZeroOrOne(self, quantifier: ZeroOrOne) -> Tuple[bool, Any]:
        _, r = self.process(quantifier.expr)
        return True, r
    
    def process_OrOp(self, or_op: OrOp) -> Tuple[bool, Any]:
        for expr in or_op.exprs:
            match, result = self.process(expr)
            if match:
                return True, result
        return False, None
    
    def parse(self, tokens: List[Token], starting_point=None):
        self.tokens = tokens
        self.index = 0
        if starting_point is None:
            starting_point = getattr(self, "starting_point", None)

        return self.pattern_match(starting_point=starting_point)
    

    def get_result_structure(self, statement: str) -> str:
        """Function to show the strucutre of data returned from a given grammar rule"""
        l = GrammarLexer()
        tokens = l.lexString(statement).tokens
        r = GrammarParser().parse(tokens)

        return self.rs(r)
    
    def rs(self, ast) -> str:
        target = f"rs_{ast.__class__.__qualname__}"
        r = getattr(self, target)(ast)
        return r
    
    def rs_Statement(self, statement: Statement) -> str:
        rv = "[ "
        for part in statement.grammar:
            rv += self.rs(part) + ", "
        rv += "]"
        return rv
    
    def rs_ExprList(self, exprList: ExprList) -> str:
        rv = "[ "
        for expr in exprList.exprs:
            rv += self.rs(expr) + ", "
        rv += "]"
        return rv

    def rs_TokenPointer(self, pointer: TokenPointer) -> str:
        return f"'{pointer.target}'"
    
    def rs_StatementPointer(self, pointer: StatementPointer) -> str:
        return f"<{pointer.target}>"
    
    def rs_ZeroOrMore(self, quantifier: ZeroOrMore) -> str:
        return f"[ {self.rs(quantifier.expr)} *... ]"
    
    def rs_OneOrMore(self, quantifier: OneOrMore) -> str:
        return f"[ OneOrMore {self.rs(quantifier.expr)} +.. ]"
    
    def rs_ZeroOrOne(self, quantifier: ZeroOrOne) -> str:
        return f"({self.rs(quantifier.expr)} or None)"
    
    def rs_OrOp(self, or_op: OrOp) -> str:
        rv = "( "
        for expr in or_op.exprs:
            rv += self.rs(expr) + " | "
        return rv[:-2] + " )"


del Parser.tokens