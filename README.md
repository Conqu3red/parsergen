# parsergen
A simple library for creating lexers and recursive descent parsers.

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
    try:
        p.parse(l.lex_string(s))
    except Exception as e:
        print(e)
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

## Overcoming issues with left recursion
Recursive descent parsers are unable to handle direct or indirect left recursion. This is an issue when writing expressions for left associative operators.
The following example is directly left recursive:
```
expr  :  expr PLUS term
```
and when attempting to process this rule it will fall into an infinite loop.
There are different ways to solve this problem, my solution is below:
```
expr  :  term (PLUS term)*
```
The disadvantage to this is that there is then some processing required after the pattern matching to reach the original desired strucutre or action.
```python
@grammar("term (PLUS term)*")
def expr(self, p):
    rv = p[0]
    for op, term in p[1]:
        rv += term
    
    return rv
```
See [here](https://en.wikipedia.org/wiki/Left_recursion) for more details.

## Writing expressions for right-associative operators
Some operators are right associative, for example the `**` operator.
Right recursion can be implemented more normally in the grammar expression:
```
expr  :  term (POW expr)?
```
This behaves as expected, after pattern matching you do have to perform a check in your code as seen next:
```python
@grammar("term (POW expr)?")
def expr(self, p):
    if p[1]:
        return p[0] ** p[1][1]
    return p[0]
```

# Printing the grammar for your parser
It is sometimes helpful to see the entire grammar for you parser. This can be done as shown below:
```python
from parsergen import get_grammar
print(get_grammar(CalcParser))
```


See `example_calc.py` and `example.py` for more examples, or look at the source code.