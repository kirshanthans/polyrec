import ast, astunparse
from pprint import pprint

def main():
    with open("examples/sources/test.py", "r") as source:
        tree = ast.parse(source.read())
        analyzer = Analyzer()
        transformer = Transformer()
        analyzer.visit(transformer.visit(tree))
        analyzer.report()

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions[node.name] = node
        self.generic_visit(node)

    def report(self):
        for f in self.functions:
            print(astunparse.unparse(self.functions[f]))

class Transformer(ast.NodeTransformer):

    def visit_Name(self, node: ast.Name):
        if node.id == "i":
            result = ast.Name()
            result.id = "j"
            result.lineno = node.lineno
            result.col_offset = node.col_offset
            return result
        return node

    def visit_arg(self, node: ast.arg):
        if node.arg == "i":
            result = ast.arg("j", node.annotation)
            return result
        return node

if __name__ == "__main__":
    main()