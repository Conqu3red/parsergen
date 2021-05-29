# parsergen
A simple library for creating parsers and lexers.

# Quickstart
```
pip install parsergen
```
## Defining a Lexer
Tokens have different regular expressions. They can also have modifier functions, for example the `INT` tokens get their values turned into an `int`.
```python
from parsergen import *
class CalcLexer(Lexer):
    
    @token(r"0x[0-9a-fA-F]+", r"[0-9]+")
    def INT(self, t):
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
```

## Creating a Parser
### Grammar Expressions
Grammar Expressions describe the syntax that can be parsed.
For our basic example calculator, you will get a terminal to type math expressions
```
> 2 + 3 * 4
14
> (2 + 3) * 4
20
> 2 ** 2 ** 3
256
```
It is important that the precedence of the arithmetic operators is correct, we have to account for this when designing our grammar rules.
Here is the grammar:
```
statement       :  assign | expr
assign          :  SET ID TO expr
expr            :  prec3
prec3           :  prec2 (ADD | SUB prec2)*
prec2           :  prec1 (MUL | DIV prec1)*
prec1           :  factor (POW prec1)?
factor          :  INT | ID
factor          :  LPAREN expr RPAREN
```
the rules `prec3` and `prec2` are left associative, whereas `prec1` is right associative because it implements the pow operator
We can then define our parser.
```python
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
    
    @grammar("prec3")
    def expr(self, p):
        return p[0]
    
    @grammar("prec2 (ADD | SUB prec2)*") # left associative
    def prec3(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "+":
                r += num
            else:
                r -= num
        return r
    
    @grammar("prec1 (MUL | DIV prec1)*") # left associative
    def prec2(self, p):
        r = p[0]
        for op, num in p[1]:
            if op == "*":
                r *= num
            else:
                r /= num
        return r
    
    @grammar("factor (POW prec1)?") # right associative
    def prec1(self, p):
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
    p.parse(l.lex_string(s))
```

### Handling Newlines
The Lexer, by default knows nothing about line numbers. You have to tell it what to do.
```python
class MyLexer(Lexer):
    @token(r"\n+")
    def NEWLINE(self, t):
        self.lineno += len(t.value)
        self.column = 0
        return t
    ...
```

See `example_calc.py` and `example.py` for more examples, or look at the source code.