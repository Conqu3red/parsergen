# parsergen
A simple library for creating lexers and PEG parsers.

[Generating Parsers](#generating-parsers)

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
expr            :  sum
sum             :  product (ADD | SUB product)*
product         :  power (MUL | DIV power)*
power           :  factor (POW power)?
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
When attempting to process this rule it will fall into an infinite loop.
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


# Implementation details
The grammar rules currently support most of the PEG parsing [syntax](https://en.wikipedia.org/wiki/Parsing_expression_grammar#Syntax).
The only rules not supported are:
- And-predicate: `&e`
- Not-predicate: `!e`

The simple calculator described implementes grammar similar to the rules seen [here](https://en.wikipedia.org/wiki/Parsing_expression_grammar#Examples)

See `example_calc.py` and `example.py` for more examples, or look at the source code.

# Generating Parsers
This module can also be used to generate parsers.
This is a more advanced use, the generated parser's grammar can even include left recursion!

By using slightly more advanced grammar expressions, we can develop the grammar rules for a simple calculator,
`examples/calc.gram:`
```
expr   :  left=expr ADD right=term   { left + right };
       :  left=expr SUB right=term   { left - right };
       :  e=term { e };

term   :  left=term MUL right=factor { left * right };
       :  left=term DIV right=factor { left * right };
       :  e=factor { e };

factor :  left=item POW right=factor { left ** right };
       :  e=item { e };

item    :  n=INT { int(n.value) };
        :  LPAREN e=expr RPAREN { e };
```
Then you can run the following to generate the parser: (you might have to use `python3` instead of `python`)
```
parsergen calc.gram -o calc_parser.py
```
## Using the generated parser
We will follow along with the example in `examples/calc.py` for how to use the generated parser.
You muse first declare the Lexer which provides the required token types.
Then you have to provide the parser a `TokenStream` of your tokenized/lexed input:
```python
from calc_parser import CustomParser as CalcParser
from parsergen import Lexer, Token, token
from parsergen.parser_utils import TokenStream

class CalcLexer(Lexer):
    INT    =  r"[0-9]+"
    ADD    =  r"\+"
    SUB    =  r"\-"
    POW    =  r"\*\*" # must be first, as is longer than 'MUL' token!
    MUL    =  r"\*"
    DIV    =  r"\/"
    LPAREN =  r"\("
    RPAREN =  r"\)"
    
    ignore = " \t"
    ignore_comment = r"\#.*"

while True:
    expr = input("> ")
    tokens = CalcLexer().lex_string(expr).tokens # get list of tokens from input
    stream = TokenStream(tokens) # create token stream
    parser = CalcParser(stream)
    print(parser.start())
```