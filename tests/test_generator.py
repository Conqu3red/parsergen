from parsergen.grammar_utils import *
from parsergen.parsergen import *
import unittest

def construct_parser(grammar: str) -> GeneratedParser:
    g = Generator()
    r = g.generate(grammar, display=False)
    exec(r, globals())
    return globals()[g.config["class_name"]]

def load_metagram() -> GeneratedParser:
    with open("parsergen/metagrammar.gram") as f:
        pgram = f.read()

    g = Generator()
    gl = GrammarLexer()
    parser_definition = parse_all(gl.lex_string(pgram))
    rules = g.process_sections(parser_definition)
    g.config["header"] = ""
    r = g.generate_parser_class(rules)
    
    exec(r, globals())
    return globals()[g.config["class_name"]]
    

class CalculatorTest(unittest.TestCase):
    def test_calculator(self):
        p = construct_parser("""
        expr  : left=expr PLUS  right=term { left + right };
              : left=expr MINUS right=term { left - right };
              : p=term { p };
        term  : p=N { float(p.value) };
        """)
        t = p(TokenStream([
            Token("N", "1"), Token("PLUS", "+"), Token("N", "2"), Token("MINUS", "-"), Token("N", "3")
        ]))
        res = t.expr()
        self.assertEqual(res, 0.0)

class AdvancedExpressionTest(unittest.TestCase):
    def test_generate(self):
        p = construct_parser("""
        expr  : (A B|C|D)+ EOF;
        """)

        t = p(TokenStream([
            Token(char, "") for char in "AB AC AD" if char != " "
        ]))
        
        expr = t.expr()
        target = Node(
            'expr', 
            [
                [
                    [Token(type='A', value=''), Token(type='B', value='')],
                    [Token(type='A', value=''), Token(type='C', value='')],
                    [Token(type='A', value=''), Token(type='D', value='')],
                ],
                Token(type='EOF', value='<EOF>', start=Pos(0, 1), end=Pos(0, 1)),
            ],
        )
        self.assertEqual(
            expr,
            target
        )
    
    def test_predicate(self):
        p = construct_parser("""
        expr  : (A B !C) EOF;
        """)
        t = p(TokenStream([Token(char, "") for char in "A B C" if char != " "]))
        self.assertIsNone(t.expr())
        
        t = p(TokenStream([Token(char, "") for char in "A B" if char != " "]))
        self.assertEqual(
            t.expr(),
            Node(
                'expr',
                [
                    [
                        Token(type='A', value=''),
                        Token(type='B', value=''),
                    ],
                    Token(type='EOF', value='<EOF>', start=Pos(0, 1), end=Pos(0, 1))
                ]
            )
        )

class MetagrammarTest(unittest.TestCase):
    def test_metagrammar(self):
        with open("parsergen/metagrammar.gram") as f:
            pgram = f.read()

        new_parser = load_metagram()

        l = GrammarLexer()
        token_stream = TokenStream(l.lex_string(pgram))
        p = new_parser(token_stream)
        result = p.parser_definition()

        expected = parse_all(l.lex_string(pgram))

        #print(result)
        #print(format_grammar(post_process(result)))

        #print(expected)
        #print(format_grammar(post_process(expected)))

        self.assertEqual(
            repr(result),
            repr(expected), 
            "The grammar parser generated from the metagrammar behaves differently to the current parser."
        )

class ErrorTest(unittest.TestCase):
    def test_error(self):
        p = construct_parser("""
        expr  : (A B C D) | (A B A D) EOF;
        """)
        t = p(TokenStream([
            Token(char, "") for char in "A B E D" if char != " "
        ]))
        self.assertIsNone(t.expr())
        self.assertEqual(t.error_pos, 2)
        self.assertIsInstance(t.error(), ParseError)