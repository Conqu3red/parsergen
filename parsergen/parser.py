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
from .grammar_parser import GrammarParser
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
    rv = r.parser_definition()
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
    return GrammarPrinter(g).format_grammar()