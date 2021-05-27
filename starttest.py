from parsergen import *
from pprint import pprint

class MyLexer(Lexer):
    tokens = {
        "PRINT":   r"PRINT",
        "INT":     r"[0-9]+",
        "ADD":     r"ADD",
        "SUB":     r"SUB",
        "MUL":     r"MUL",
        "DIV":     r"DIV",
        "SET":     r"SET",
        "TO":      r"TO",
        "ID":      r"[A-Za-z_]+",
        "LPAREN":  r"\(",
        "RPAREN":  r"\)",
        "NEWLINE": r"\n",
    }
    ignore = " \t"

"""
statement_list  :  statement*
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

    @Parser.grammar("statement_list  :  (statement NEWLINE*)*")
    def statement_list(self, p):
        print(p)
        return p
        #return "\n".join(p[0][0])
    
    @Parser.grammar("statement  :  INT")
    def statement(self, p):
        return p[0]

l = MyLexer()
p = MyParser()

#pprint(p._grammar)

pprint(l.lexString("""1\n2\n""").tokens)
print(p.parse(l.lexString("""1\n2\n""").tokens, starting_point="statement_list"))
# statement_list is broken
