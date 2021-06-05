from parsergen import *
from pprint import pprint

class CalcLexer(Lexer):
    
    @token(r"0x[0-9a-fA-F]+", r"[0-9]+")
    def INT(self, t: Token):
        if t.value.startswith("0x"):
            t.value = int(t.value[2:], base=16)
        else:
            t.value = int(t.value)
        return t

    ADD    =  r"\+"
    SUB    =  r"\-"
    POW    =  r"\*\*" # must be first, as is longer than 'MUL' token!
    MUL    =  r"\*"
    DIV    =  r"\/"
    SET    =  r"set"
    TO     =  r"to"
    ID     =  r"[A-Za-z_]+"
    LPAREN =  r"\("
    RPAREN =  r"\)"
    
    ignore = " \t"
    ignore_comment = r"\#.*"

"""
statement       :  assign | expr
assign          :  SET ID TO expr
expr            :  sum
sum             :  product (ADD | SUB product)*
product         :  power (MUL | DIV power)*
power           :  factor (POW power)?
factor          :  INT | ID
factor          :  LPAREN expr RPAREN
"""

class CalcParser(Parser):

    tokens = CalcLexer.tokens
    starting_point = "statement"

    def __init__(self):
        self.names = {}

    @grammar("assign | expr")
    def statement(self, p):
        print(p[0])
    
    @grammar("SET ID TO expr")
    def assign(self, p):
        self.names[p[1]] = p[3]
    
    @grammar("sum")
    def expr(self, p):
        return p[0]
    
    @grammar("product (ADD | SUB product)*") # left associative
    def sum(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "+":
                r += num
            else:
                r -= num
        return r
    
    @grammar("power (MUL | DIV power)*") # left associative
    def product(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "*":
                r *= num
            else:
                r /= num
        return r
    
    @grammar("factor (POW power)?") # right associative
    def power(self, p):
        if p[1]:
            return p[0] ** p[1][1]
        return p[0]
    
    @grammar("INT")
    def factor(self, p):
        return p[0]
    
    @grammar("ID")
    def factor(self, p):
        try:
            return self.names[p[0]]
        except KeyError:
            raise Exception(f"variable '{p[0]}' is not defined.")

    @grammar("LPAREN expr RPAREN")
    def factor(self, p):
        return p[1]

# We can then create a simple runtime loop
l = CalcLexer()
p = CalcParser()

while True:
    s = input("> ")
    l_result = l.lex_string(s)
    try:
        p.parse(l.lex_string(s))
    except Exception as e:
        print(e)