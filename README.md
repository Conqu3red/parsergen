# parsergen
A simple library for creating lexers and PEG parsers.

[Generating Parsers](#generating-parsers)

# Quickstart
```
pip install parsergen
```
## Defining a Lexer
Tokens have different regular expressions. They can also have modifier functions, for example the `INT` tokens get their values turned into an `int` (note that changing the value property of a token to a non-string value may cause errors in some cases).
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

# Implementation details
The grammar rules currently support all of the PEG parsing [syntax](https://en.wikipedia.org/wiki/Parsing_expression_grammar#Syntax).

The simple calculator described implementes grammar similar to the rules seen [here](https://en.wikipedia.org/wiki/Parsing_expression_grammar#Examples)

See `example_calc.py` and `example.py` for more examples, or look at the source code.

# Generating Parsers
This module can also be used to generate parsers.
This is a more advanced use, the generated parser's grammar can even include left recursion!

By using slightly more advanced grammar expressions, we can develop the grammar rules for a simple calculator,
`examples/calc.gram:`
```
@class_name = 'CalcParser'

expr   :  left=expr ADD right=term   { left + right };
       :  left=expr SUB right=term   { left - right };
       :  e=term { e };

term   :  left=term MUL right=factor { left * right };
       :  left=term DIV right=factor { left / right };
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
from calc_parser import CalcParser
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
    lexer_result = CalcLexer().lex_string(expr) # get LexerResult from input
    stream = TokenStream(lexer_result) # create token stream
    parser = CalcParser(stream)
    result = parser.start()
    error = parser.error()
    if result is None and error is not None:
        print(error) # error handling
    else:
        print(result)
```

## Configuration
You can declare config options by doing `@identifier = 'value'`
Options:
- `@class_name` - name of the generated class, default `'CustomParser'`
- `@inherits_from` - class that your generated parser inherits from, defualt `'GeneratedParser'`.
    Set this value to your own class that inherits from `GeneratedParser` to add more advanced functionality.
- `@header` - python lines that are included at the top of the generated parser, default is nothing.