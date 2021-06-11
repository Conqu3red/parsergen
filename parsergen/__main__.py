from .parsergen import *
from . import __version__
import argparse

def main():
    p = argparse.ArgumentParser("parsergen")
    p.add_argument("file", type=argparse.FileType('r'))
    p.add_argument("-o", type=str, default="generated_parser.py", metavar="outfile")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args()
    grammar = args.file.read()

    generator = Generator()

    result = generator.generate(grammar)
    with open(args.o, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()