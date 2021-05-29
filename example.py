from parsergen import *
from pprint import pprint

class MyLexer(Lexer):
    @token(r"\n+")
    def NEWLINE(self, v):
        self.lineno += len(v.value)
        self.column = 0
        return v
    
    PRINT  =  r"PRINT"
    INT    =  r"[0-9]+"
    ADD    =  r"ADD"
    SUB    =  r"SUB"
    MUL    =  r"MUL"
    DIV    =  r"DIV"
    SET    =  r"SET"
    TO     =  r"TO"
    ID     =  r"[A-Za-z_]+"
    LPAREN =  r"\("
    RPAREN =  r"\)"
    
    ignore = " \t"

"""
statement_list  :  (statement NEWLINE*)*
statement       :  print | assign
print           :  PRINT LPAREN expr RPAREN
assign          :  SET ID TO expr
expr            :  term2
term2           :  term (ADD | SUB term)*
term            :  factor (MUL | DIV factor)*
factor          :  INT
factor          :  LPAREN expr RPAREN
"""

class MyParser(Parser):

    tokens = MyLexer.tokens
    starting_point = "statement_list"

    @grammar("statement_list  :  (statement NEWLINE*)*")
    def statement_list(self, p):
        return "\n".join([e[0] for e in p[0]])
    
    @grammar("statement  :  print | assign")
    def statement(self, p):
        return p[0]

    @grammar("print  : PRINT LPAREN expr RPAREN")
    def print_statement(self, p):
        return f"print({p[2]})"
    
    @grammar("assign  :  SET ID TO expr")
    def assign(self, p):
        return f"{p[1]} = {p[3]}"
    
    @grammar("expr  :  term_two")
    def expr(self, p):
        return p[0]
    
    @grammar("term_two  :  term (ADD | SUB term)*")
    def t2(self, p):
        r = p[0]
        convert = {"ADD": "+", "SUB": "-"}
        for op, num in p[1]:
            r += f" {convert[op]} {num}"
        if len(p[1]) > 0:
            r = f"({r})"
        return r
    
    @grammar("term  :  factor (MUL | DIV factor)*")
    def t(self, p):
        r = p[0]
        convert = {"MUL": "*", "DIV": "/"}
        for op, num in p[1]:
            r += f" {convert[op]} {num}"
        if len(p[1]) > 0:
            r = f"({r})"
        return r
    
    @grammar("factor  :  INT")
    def factor(self, p):
        return p[0]
    
    @grammar("factor  :  LPAREN expr RPAREN")
    def factor2(self, p):
        return "(" + p[1] + ")"

l = MyLexer()
p = MyParser()

print(p.parse(l.lex_string("PRINT(1 ADD 2 ADD 3)")))
print(p.parse(l.lex_string("SET a TO 2 ADD 3 MUL 4")))

t = l.lex_string("""SET a TO 2 ADD 3 MUL 4\nSET b TO 1 DIV 2 DIV 3""")
pprint(t.tokens)
pprint(t.lines)
r = p.parse(l.lex_string("""SET a TO 2 ADD 3 MUL 4\nSET b TO 1 DIV 2 DIV 3"""))
print(r)

print(MyParser().get_result_structure("statement_list  :  (statement NEWLINE*)*"))