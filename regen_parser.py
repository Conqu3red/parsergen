from parsergen.parsergen import Generator

HEADER = """from .grammar_utils import *

"""

with open("parsergen/metagrammar.gram") as f:
    grammar = f.read()

result = Generator().generate(grammar)

with open("parsergen/grammar_parser.py", "w") as f:
    f.write(HEADER + result)