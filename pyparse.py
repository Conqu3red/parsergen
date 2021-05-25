"""
Grammar for the grammar:
Tokens:
    ID      :   [a-z]+
    TOKEN   :   [A-Z]+



statement  :  ID COLON (expr)*
expr       :  item
expr       :  expr OR expr
expr       :  expr STAR
expr       :  expr PLUS
expr       :  LPAREN expr RPAREN

item       :  ID | TOKEN
"""
from pprint import pprint
from lexer import *
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
    def __init__(self) -> None:
        raise NotImplemented

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

tests = """statement  :  ID COLON (expr)*
expr       :  item
expr       :  expr OR expr
expr       :  expr STAR
expr       :  expr PLUS
expr       :  LPAREN expr RPAREN
item       :  ID | TOKEN""".split("\n")

#for t in tests:
#    print(t)
#    l = GrammarLexer()
#    tokens = l.lexString(t).tokens
#    p = GrammarParser()
#    print(p.parse(tokens))

@overload
def grammar(statement: str):
    pass

class StatementAndTarget(NamedTuple):
    statement: Statement
    function: Any

class Parser:
    _grammar: Dict[str, List[StatementAndTarget]] = {}

    def grammar(statement):
        #print(f"grammar {statement}")
        l = GrammarLexer()
        tokens = l.lexString(statement).tokens
        r = GrammarParser().parse(tokens)
        
        
        def inner(func):
            if r.name not in Parser._grammar:
                Parser._grammar[r.name] = [StatementAndTarget(statement=r, function=func)]
            else:
                Parser._grammar[r.name].append(StatementAndTarget(statement=r, function=func))
            
            return func
        
        return inner
    
    @property
    def current_token(self) -> Token:
        return self.tokens[self.index]
    
    def pattern_match(self, starting_point=None) -> List[Any]:
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
        #print(target, "  ", ast)
        return getattr(self, target)(ast)
    
    def process_StatementAndTargetList(self, statements: List[StatementAndTarget]) -> Tuple[bool, Any]:
        for statement, func in statements:
            i = self.index
            try:
                matched, result = self.process(statement)
                if matched:
                    return True, func(self, result)
            except IndexError:
                pass
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
        try:
            for expr in exprList.exprs:
                matched, r = self.process(expr)
                result.append(r)
                if not matched:
                    break
            else:
                return True, result
        except IndexError:
            pass
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
            #print("ZeroOrMore check for", quantifier.expr)
            match, r = self.process(quantifier.expr)
            #print("ZeroOrMore", match, r, self.current_token)
            if match:
                result.append(r)
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
    
    def process_OrOp(self, or_op: OrOp) -> Tuple[bool, Any]:
        for expr in or_op.exprs:
            match, result = self.process(expr)
            if match:
                return True, result
        return False, None
    
    def parse(self, tokens: List[Token], starting_point=None):
        self.tokens = tokens
        self.index = 0
        return self.pattern_match(starting_point=starting_point)