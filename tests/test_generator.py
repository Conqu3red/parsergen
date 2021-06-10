from parsergen import *
from parsergen.parsergen import *

### calc test ###
g = Generator()
r = g.generate("""
expr  : left=expr PLUS  right=term { left + right };
      : left=expr MINUS right=term { left - right };
      : p=term { p };
term  : p=N { float(p.value) };
""")
print(r)
exec(r)

t = CustomParser(TokenStream([
    Token("N", "1"), Token("PLUS", "+"), Token("N", "2"), Token("MINUS", "-"), Token("N", "3")
]))
res = t.expr()
assert res == 0.0
print(res)



### advanced expression test ###
g = Generator()
r = g.generate("""
expr  : (A B|C|D)+ EOF;
""")
print(r)
exec(r)
t = CustomParser(TokenStream([
    Token(char, "") for char in "AB AC AD" if char != " "
]))
print(t.expr())


### metagrammar test ###
g = Generator()
with open("parsergen/metagrammar.gram") as f:
    pgram = f.read()

r = g.generate(pgram)
print(r)
exec(r)

l = GrammarLexer()
token_stream = TokenStream(l.lex_string(pgram)) #broken?
p = CustomParser(token_stream)
result = p.statement_list()

expected = parse_all(l.lex_string(pgram))

#print(result)
print(format_grammar(post_process(result)))

#print(expected)
print(format_grammar(post_process(expected)))

assert repr(post_process(result)) == repr(post_process(expected))
#print(token_stream.peek_token())




### ERROR TEST ###
g = Generator()
r = g.generate("""
expr  : (A B C D) | (A B A D) EOF;
""")
print(r)
exec(r)
t = CustomParser(TokenStream([
    Token(char, "") for char in "A B E D" if char != " "
]))
print(t.expr())
print(t.error_pos, t.error())