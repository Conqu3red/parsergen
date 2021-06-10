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
    lexer_result = CalcLexer().lex_string(expr) # get LexerResult from input
    stream = TokenStream(lexer_result) # create token stream
    parser = CalcParser(stream)
    result = parser.start()
    error = parser.error()
    if result is None and error is not None:
        print(error) # error handling
    else:
        print(result)