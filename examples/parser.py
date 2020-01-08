import sys
from pycparser import c_parser, c_ast

with open('examples/c_files/test.c', 'r') as f:
    text = f.read()

parser = c_parser.CParser()
ast = parser.parse(text)
ast.show()
