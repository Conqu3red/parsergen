from parsergen import *
from pprint import pprint

class CalcLexer(Lexer):
    tokens = {
        "INT":     (r"[0-9]+", lambda _, x: int(x)),
        "ADD":     r"\+",
        "SUB":     r"\-",
        "POW":     r"\*\*",
        "MUL":     r"\*",
        "DIV":     r"\/",
        "SET":     r"set",
        "TO":      r"to",
        "ID":      r"[A-Za-z_]+",
        "LPAREN":  r"\(",
        "RPAREN":  r"\)",
    }
    ignore = " \t"

"""
statement       :  assign | expr
assign          :  SET ID TO expr
expr            :  prec3
prec3           :  prec2 (ADD | SUB prec2)*
prec2           :  prec1 (MUL | DIV prec1)*
prec1           :  factor (POW prec1)?
factor          :  INT | ID
factor          :  LPAREN expr RPAREN
"""

class CalcParser(Parser):

    tokens = CalcLexer.tokens
    starting_point = "statement"

    def __init__(self):
        self.names = {}

    @grammar("statement  :  assign | expr")
    def statement(self, p):
        print(p[0])
    
    @grammar("assign  :  SET ID TO expr")
    def assign(self, p):
        self.names[p[1]] = p[3]
    
    @grammar("expr  :  prec3")
    def expr(self, p):
        return p[0]
    
    @grammar("prec3  :  prec2 (ADD | SUB prec2)*") # left associative
    def prec3(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "+":
                r += num
            else:
                r -= num
        return r
    
    @grammar("prec2  :  prec1 (MUL | DIV prec1)*") # left associative
    def prec2(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "*":
                r *= num
            else:
                r /= num
        return r
    
    @grammar("prec1  :  factor (POW prec1)?") # right associative
    def prec1(self, p):
        if p[1]:
            return p[0] ** p[1][1]
        return p[0]
    
    @grammar("factor  :  INT")
    def int_factor(self, p):
        return p[0]
    
    @grammar("factor  :  ID")
    def id_factor(self, p):
        try:
            return self.names[p[0]]
        except KeyError:
            raise Exception(f"variable '{p[0]}' is not defined.")

    @grammar("factor  :  LPAREN expr RPAREN")
    def bracket_factor(self, p):
        return p[1]

l = CalcLexer()
p = CalcParser()

while True:
    s = input("> ")
    l_result = l.lexString(s)
    p.parse(l.lexString(s))