from pyparse import *

class MyLexer(Lexer):
    tokens = {
        "N":     r"[0-9]+",
        "PLUS":  r"\+"
    }
    ignore = " \t"

class MyParser(Parser):

    tokens = MyLexer.tokens

    @Parser.grammar("expr : term_five")
    def expr(self, p):
        return ("expr", p[0])
    
    @Parser.grammar("term_five : factor (PLUS factor)*")
    def expr(self, p):
        if len(p[1]) > 0:
            return ('BinOp', p[0], p[1])
        return p[0]
    
    @Parser.grammar("factor : N")
    def factor(self, p):
        return ('num', p[0])
    
    @Parser.grammar("uplus : PLUS expr")
    def uplus(self, p):
        return ('uplus', p[1])
    

l = MyLexer()
p = MyParser()

pprint(p._grammar)

print(p.parse(l.lexString("1 + 2").tokens))
print(p.parse(l.lexString("+2").tokens))