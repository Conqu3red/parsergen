from parsergen import *
from parsergen.parsergen import *

g = Generator()
r = g.generate("""
expr  : left=expr PLUS  right=term { left + right };
      : left=expr MINUS right=term { left - right };
      : p=term { p };
term  : p=N { float(p.value) };
""")
print(r)
exec(r)



t = TempParser(TokenStream([
    Token("N", "1"), Token("PLUS", "+"), Token("N", "2"), Token("MINUS", "-"), Token("N", "3")
]))
print(t.expr())
# need to add support for adding code actions like
# term : N { float(p[0].value) }

# would also like to support the mode that uses decorators and functions to define return values??

g = Generator()
r = g.generate("""
expr  : (A B|C|D)+ EOF;
""")
#print(r)
exec(r)
t = TempParser(TokenStream([
    Token(char, "") for char in "AB AC AD" if char != " "
]))
print(t.expr())

# need to write out meta-grammar and then use that as the grammar parser