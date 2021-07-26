"""Parses grammar expressions and performs pattern matching

Tokens:
    ID      :   [a-z0-9_]+
    TOKEN   :   [A-Z0-9_]+


Grammar:

statement_list : statement* EOF;
statement      :  (ID? COLON)? expr*;
expr_list      :  expr*;
expr           :  (ID EQ)? prec4;
prec4          :  prec3 (OR prec3)*;
prec3          :  prec2 STAR?;
prec2          :  prec1 PLUS?;
prec1          :  factor QMARK?;

factor         :  LPAREN expr_list RPAREN;
               :  item;
item           :  ID | TOKEN;
"""
from .lexer import *
from .utils import *
from typing import *
from .grammar_parser import *
from .grammar_parser import CustomParser as GrammarParser
from .parser_utils import ParseError


def parse_statement(lexer_result: LexerResult):
    r = GrammarParser(TokenStream(lexer_result))
    rv = r.statement()
    err = r.error()
    if rv is None and err is not None:
        raise err
    return rv

def parse_all(lexer_result: LexerResult):
    r = GrammarParser(TokenStream(lexer_result))
    rv = r.statement_list()
    err = r.error()
    if rv is None and err is not None:
        raise err
    return rv

def post_process(rules_list: List[Statement]) -> Dict[str, List[Statement]]:
    rules = {}
    current_name = "<>"
    for r in rules_list:
        if r.name == "<>":
            r.name = current_name
        else:
            current_name = r.name
        if r.name in rules:
            rules[r.name].append(r)
        else:
            rules[r.name] = [r]
    return rules

class StatementAndTarget(NamedTuple):
    statement: Statement
    function: Any


def grammar(statement: str):
    """decorator for declaring grammar rules/statements"""
    if not statement.rstrip().endswith(";"):
        statement += ";"
    def inner(func):
        l = GrammarLexer()
        result = l.lex_string(statement)
        r = parse_statement(result)
        if r.name == "<>":
            r.name = func.__name__
        func._rule = r

        return func
    
    return inner


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
            return Token("__EOF__", "<EOF>")
    
    def error(self) -> ParseError:
        return ParseError(
            f"Unexpected token {self.current_token.error_format()}", 
            *self.current_token.pos,
            lineText=self.lines[self.current_token.lineno-1] if self.current_token.lineno <= len(self.lines) else ""
        )


    def pattern_match(self, starting_point=None) -> List[Any]:
        self.indent = 0
        if starting_point is not None:
            matched, result, err = self.process_StatementAndTargetList(self._grammar[starting_point])
            if matched:
                return result
            elif err:
                raise err
            return
        
        for identifier in self._grammar:
            matched, result, err = self.process_StatementAndTargetList(self._grammar[identifier])
            if matched:
                return result
            elif err:
                raise err

    def process(self, ast: AST) -> Tuple[bool, Any, Optional[ParseError]]:
        target = f"process_{ast.__class__.__qualname__}"
        #print(self.indent * "|" + target, " ", ast)
        self.indent += 1
        r = getattr(self, target)(ast)
        self.indent += -1
        #print(self.indent * "|" + target, "RET ", ast, r)
        return r
    
    def process_StatementAndTargetList(self, statements: List[StatementAndTarget]) -> Tuple[bool, Any, Optional[ParseError]]:
        err = None
        for statement, func in statements:
            i = self.index
            matched, result, err = self.process(statement)
            if matched:
                return True, func(self, result), err
            self.index = i
        
        return False, None, err
    
    def process_Statement(self, statement: Statement) -> Tuple[bool, List[Any]]:
        result = []
        err = None
        for part in statement.grammar:
            matched, r, err = self.process(part)
            result.append(r)
            if not matched:
                break
        else:
            return True, result, err
        return False, [], err
    
    def process_ExprList(self, exprList: ExprList) -> Tuple[bool, List[Any]]:
        result = []
        err = None
        i = self.index
        for expr in exprList.exprs:
            matched, r, err = self.process(expr)
            result.append(r)
            if not matched:
                break
        else:
            return True, result, err
        self.index = i
        return False, [], err

    def process_TokenPointer(self, pointer: TokenPointer) -> Tuple[bool, Any, Optional[ParseError]]:
        if self.current_token.type == pointer.target:
            rv = True, self.current_token.value, None
            self.index += 1
        else:
            return False, None, self.error()
        return rv
    
    def process_StatementPointer(self, pointer: StatementPointer) -> Tuple[bool, Any, Optional[ParseError]]:
        return self.process_StatementAndTargetList(self._grammar[pointer.target])
    
    def process_ZeroOrMore(self, quantifier: ZeroOrMore) -> Tuple[bool, Any, Optional[ParseError]]:
        result = []
        match = True
        while match:
            match, r, err = self.process(quantifier.expr)
            if match:
                result.append(r)
            else:
                break
        return True, result, None
    
    def process_OneOrMore(self, quantifier: OneOrMore) -> Tuple[bool, Any, Optional[ParseError]]:
        result = []
        match = True
        err = None
        while match:
            match, r, err = self.process(quantifier.expr)
            if match:
                result.append(r)
        if len(result) == 0:
            return False, result, err
        return True, result, None
    
    def process_ZeroOrOne(self, quantifier: ZeroOrOne) -> Tuple[bool, Any, Optional[ParseError]]:
        _, r, err = self.process(quantifier.expr)
        return True, r, err
    
    def process_OrOp(self, or_op: OrOp) -> Tuple[bool, Any, Optional[ParseError]]:
        err = None
        for expr in or_op.exprs:
            match, result, err = self.process(expr)
            if match:
                return True, result, err
        return False, None, err
    
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
            raise self.error()
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
        result = l.lex_string(statement)
        r = parse_statement(result)

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
    def __init__(self, _grammar) -> None:
        self._grammar = _grammar
    
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
        if statement.action:
            rv += " { " + statement.action + " }"
        return rv + ";"
    
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
    
    def process_ConstantString(self, cs: ConstantString) -> str:
        return repr(cs.value)
    
    def process_ZeroOrMore(self, q: ZeroOrMore) -> str:
        return self.process(q.expr) + "*"
    
    def process_OneOrMore(self, q: OneOrMore) -> str:
        return self.process(q.expr) + "+"
    
    def process_ZeroOrOne(self, q: ZeroOrOne) -> str:
        return self.process(q.expr) + "?"
    
    def process_AndPredicate(self, p: AndPredicate) -> str:
        return "&" + self.process(p.expr)
    
    def process_NotPredicate(self, p: NotPredicate) -> str:
        return "!" + self.process(p.expr)
    
    def process_ExprList(self, expr_list: ExprList) -> str:
        rv = "("
        for c, part in enumerate(expr_list.exprs):
            if c != 0:
                rv += " "
            rv += self.process(part)
        return rv + ")"
    
    def process_NamedItem(self, item: NamedItem) -> str:
        return f"{item.name}={self.process(item.expr)}"
    
    def format_grammar(self) -> str:
        result = ""
        gap = max([len(name) for name in self._grammar])
        for name, rules in self._grammar.items():
            if len(rules) <= 1:
                result += f"{name}  :  "
            else:
                result += f"{name}\n    :  "
            
            for c, rule in enumerate(rules):
                s = self.process(rule)
                if c != 0:
                    result += "    :  "
                result += f"{s}\n"
        return result

def format_grammar(g) -> str:
    if isinstance(g, Parser):
        g = g._grammar
    return GrammarPrinter(g).format_grammar()