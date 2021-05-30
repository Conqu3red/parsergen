"""Parses grammar expressions and performs pattern matching

Tokens:
    ID      :   [a-z0-9_]+
    TOKEN   :   [A-Z0-9_]+


Grammar:

statement  :  (ID COLON)? expr*
expr_list  :  expr*
expr       :  prec3 (OR prec3)*
prec3      :  prec2 STAR?
prec2      :  prec1 PLUS?
prec1      :  factor QMARK?

factor     :  LPAREN expr_list RPAREN
factor     :  item

item       :  ID | TOKEN
"""
from .lexer import *
from .utils import *
from typing import *


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
    ID =      r"[a-z0-9_]+"
    TOKEN =   r"[A-Z0-9_]+"
    COLON =   r"\:"
    OR =      r"\|"
    STAR =    r"\*"
    PLUS =    r"\+"
    QMARK =   r"\?"
    LPAREN =  r"\("
    RPAREN =  r"\)"
    NEWLINE = r"\n"
    
    ignore = " \t"


class GrammarParser(object):
    """Parses grammar expressions/rules into and AST"""
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
    
    @property
    def next_token(self):
        if len(self.tokens) > 1:
            return self.tokens[1]
        return self.eof()

    def statement(self) -> Statement:
        "(ID COLON)? (expr)*"
        token = self.current_token
        name = "_"
        if self.current_token.type == "ID" and self.next_token.type == "COLON":
            self.eat("ID")
            name = token.value
            self.eat("COLON")
        expr = []
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
        "expr  :  prec3 (OR prec3)*"
        node = self.prec3()
        if self.current_token.type == "OR":
            exprs = [node]
            while self.current_token.type == "OR":
                self.eat("OR")
                exprs.append(self.expr())
            
            return OrOp(exprs=exprs)
        return node
    
    def prec3(self):
        "prec3  :  prec2 STAR?"
        node = self.prec2()
        if self.current_token.type == "STAR":
            self.eat("STAR")
            return ZeroOrMore(expr=node)
        return node

    def prec2(self):
        "prec2  :  prec1 PLUS?"
        node = self.prec1()
        if self.current_token.type == "PLUS":
            self.eat("PLUS")
            return OneOrMore(expr=node)
        return node
    
    def prec1(self):
        "prec1  :  item QMARK?"
        node = self.item()
        if self.current_token.type == "QMARK":
            self.eat("QMARK")
            return ZeroOrOne(expr=node)
        return node

    def item(self):
        """
        item  :  ID | TOKEN
              |  LPAREN expr_list RPAREN
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


def grammar(statement: str):
    """decorator for declaring grammar rules/statements"""
    
    def inner(func):
        l = GrammarLexer()
        tokens = l.lex_string(statement).tokens
        r = GrammarParser().parse(tokens)
        if r.name == "_":
            r.name = func.__name__
        func._rule = r

        return func
    
    return inner

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


class ParserMetaDict(dict):
    """Special dictionary to allow definition of the same function name multiple times in the Parser"""
    def __setitem__(self, k, v) -> None:
        if hasattr(v, "_rule") and k != "_grammar":
            r = v._rule
            if r.name not in self["_grammar"]:
                self["_grammar"][r.name] = [StatementAndTarget(statement=r, function=v)]
            else:
                self["_grammar"][r.name].append(StatementAndTarget(statement=r, function=v))
            return
        return super().__setitem__(k, v)


class ParserMeta(RequiredAttributes("tokens")):
    @classmethod
    def __prepare__(meta, name, bases):
        d = ParserMetaDict()
        d["grammar"] = grammar
        d["_grammar"] = {}
        return d

class Parser(metaclass=ParserMeta):
    """Pattern matching Parser for grammar rules"""
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
    
    @overload
    def parse(self, obj: LexerResult, starting_point=None) -> List:
        ...
    
    @overload
    def parse(self, obj: List[Token], starting_point=None) -> List:
        ...
    
    def parse(self, obj, starting_point=None) -> List:
        if isinstance(obj, LexerResult):
            tokens = obj.tokens
            lines = obj.lines
        else:
            tokens = obj
            lines = []
        self.tokens = tokens
        self.lines = lines
        self.index = 0
        if starting_point is None:
            starting_point = getattr(self, "starting_point", None)

        rv = self.pattern_match(starting_point=starting_point)
        if self.current_token.type != "__EOF__":
            if self.lines:
                raise ParseError(
                    f"Unexpected token {self.current_token.error_format()}", 
                    *self.current_token.pos,
                    lineText=self.lines[self.current_token.lineno-1]
                )
            raise ParseError(
                f"Unexpected token {self.current_token.error_format()}", 
                *self.current_token.pos
            )
        
        return rv

    @classmethod
    def get_result_structure(cls, statement: str) -> str:
        """Function to show the strucutre of data returned from a given grammar rule
        
        Example
        -------
        >>> Parser.get_result_structure("statement_list  :  (statement NEWLINE* )*")
        "[ [ [ <statement>, [ 'NEWLINE' *... ], ] *... ], ]"
        
        """
        l = GrammarLexer()
        tokens = l.lex_string(statement).tokens
        r = GrammarParser().parse(tokens)

        return cls.rs(r)
    
    @classmethod
    def rs(cls, ast) -> str:
        target = f"rs_{ast.__class__.__qualname__}"
        r = getattr(cls, target)(ast)
        return r
    
    @classmethod
    def rs_Statement(cls, statement: Statement) -> str:
        rv = "[ "
        for part in statement.grammar:
            rv += cls.rs(part) + ", "
        rv += "]"
        return rv
    
    @classmethod
    def rs_ExprList(cls, exprList: ExprList) -> str:
        rv = "[ "
        for expr in exprList.exprs:
            rv += cls.rs(expr) + ", "
        rv += "]"
        return rv
    
    @classmethod
    def rs_TokenPointer(cls, pointer: TokenPointer) -> str:
        return f"'{pointer.target}'"
    
    @classmethod
    def rs_StatementPointer(cls, pointer: StatementPointer) -> str:
        return f"<{pointer.target}>"
    
    @classmethod
    def rs_ZeroOrMore(cls, quantifier: ZeroOrMore) -> str:
        return f"[ {cls.rs(quantifier.expr)} *... ]"
    
    @classmethod
    def rs_OneOrMore(cls, quantifier: OneOrMore) -> str:
        return f"[ OneOrMore {cls.rs(quantifier.expr)} +.. ]"
    
    @classmethod
    def rs_ZeroOrOne(cls, quantifier: ZeroOrOne) -> str:
        return f"({cls.rs(quantifier.expr)} or None)"
    
    @classmethod
    def rs_OrOp(cls, or_op: OrOp) -> str:
        rv = "( "
        for expr in or_op.exprs:
            rv += cls.rs(expr) + " | "
        return rv[:-2] + " )"


del Parser.tokens

class GrammarPrinter:
    def __init__(self, parser: Parser) -> None:
        self.parser = parser
    
    def process(self, ast):
        target = f"process_{ast.__class__.__qualname__}"
        r = getattr(self, target)(ast)
        return r

    def process_StatementAndTarget(self, ast: StatementAndTarget) -> str:
        return self.process(ast.statement)
    
    def process_Statement(self, statement: Statement) -> str:
        rv = ""
        for c, part in enumerate(statement.grammar):
            if c != 0:
                rv += " "
            rv += self.process(part)
        return rv
    
    def process_OrOp(self, or_op: OrOp) -> str:
        rv = ""
        for c, part in enumerate(or_op.exprs):
            if c != 0:
                rv += " | "
            rv += self.process(part)
        return rv
        
    def process_StatementPointer(self, sp: StatementPointer) -> str:
        return sp.target
    
    def process_TokenPointer(self, tp: TokenPointer) -> str:
        return tp.target
    
    def process_ZeroOrMore(self, q: ZeroOrMore) -> str:
        return self.process(q.expr) + "*"
    
    def process_OneOrMore(self, q: OneOrMore) -> str:
        return self.process(q.expr) + "+"
    
    def process_ZeroOrOne(self, q: ZeroOrOne) -> str:
        return self.process(q.expr) + "?"
    
    def process_ExprList(self, expr_list: ExprList) -> str:
        rv = "("
        for c, part in enumerate(expr_list.exprs):
            if c != 0:
                rv += " "
            rv += self.process(part)
        return rv + ")"
    
    def get_grammar(self) -> str:
        result = ""
        gap = max([len(name) for name in self.parser._grammar])
        for name, rules in self.parser._grammar.items():
            result += name + (gap-len(name))*" " + "  :  "
            for c, rule in enumerate(rules):
                s = self.process(rule)
                if c != 0:
                    result += gap*" " + "  |  "
                result += f"{s}\n"
        return result

def get_grammar(parser: Parser) -> str:
    return GrammarPrinter(parser).get_grammar()