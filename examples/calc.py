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