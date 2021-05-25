from pyparse import *

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
    
    @Parser.grammar("statement       :  print | assign")
    def statement(self, p):
        return p[0]

    @Parser.grammar("print  : PRINT LPAREN expr RPAREN")
    def print_statement(self, p):
        return f"print({p[2]})"
    
    @Parser.grammar("assign  :  SET ID TO expr")
    def assign(self, p):
        return f"{p[1]} = {p[3]}"
    
    @Parser.grammar("expr  :  term_two")
    def expr(self, p):
        return p[0]
    
    @Parser.grammar("term_two : term (ADD | SUB term)*")
    def expr(self, p):
        r = f"({p[0]}"
        convert = {"ADD": "+", "SUB": "-"}
        for op, num in p[1]:
            r += f" {convert[op]} {num}"
        r += ")"
        return r
    
    @Parser.grammar("term : factor (MUL | DIV factor)*")
    def expr(self, p):
        r = f"({p[0]}"
        convert = {"MUL": "*", "DIV": "/"}
        for op, num in p[1]:
            r += f" {convert[op]} {num}"
        r += ")"
        return r
    
    @Parser.grammar("factor  :  INT")
    def factor(self, p):
        return p[0]
    
    @Parser.grammar("factor  :  LPAREN expr RPAREN")
    def factor(self, p):
        return p[1]

l = MyLexer()
p = MyParser()

#pprint(p._grammar)
print(p.parse(l.lexString("PRINT(1 ADD 2 ADD 3)").tokens))
print(p.parse(l.lexString("2 ADD 2").tokens))
print(p.parse(l.lexString("SET a TO 2 ADD 3 MUL 4").tokens))

pprint(l.lexString("""SET a TO 2 ADD 3 MUL 4\nPRINT(1)""").tokens)
print(p.parse(l.lexString("""SET a TO 2 ADD 3 MUL 4\nSET b TO 5""").tokens, starting_point="statement_list"))
# statement_list is broken
