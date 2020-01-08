from polyrec.lexer import Lexer
from polyrec.parser import Parser

text = """
4 + 2 + 2
"""
lexer = Lexer().get_lexer()
tokens = lexer.lex(text)

pg = Parser()
pg.parse()
parser = pg.get_parser()
ast = parser.parse(tokens)
print(ast.codegen())