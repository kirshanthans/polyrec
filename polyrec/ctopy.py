from pycparser import c_parser, c_ast
from polyrec.pygen import PyGen

class ExtractFunc(c_ast.NodeVisitor):
    def __init__(self):
        self.functions = [] # function asts

    def visit_FuncDef(self, node: c_ast.FuncDef):
        self.functions.append(node)

class CtoPy():
    def __init__(self, ast):
        self.cast = ast
        
    def getPy(self):
        extract = ExtractFunc()
        extract.visit(self.cast)
        pygen = PyGen()
        fs = ''
        for f in extract.functions:
            s = pygen.visit(f)
            s = s.replace("int i", "i: int")
            s = s.replace("Node *n", "n: Node")
            s = s.replace("!n", "n == None")
            s = s.replace("void", "def")
            s = s.replace("\n", " -> None:", 1)
            fs += s
        return fs
        

if __name__ == "__main__":
    with open("examples/sources/loop-rec.c", "r") as source:
        parser = c_parser.CParser()
        ast = parser.parse(source.read())
        ctopy = CtoPy(ast)
        print(ctopy.getPy())