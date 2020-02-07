import ast, astunparse, copy
from pprint import pprint

def main():
    with open("examples/sources/test.py", "r") as source:
        tree = ast.parse(source.read())
        analyzer = Analyzer()
        transformer = ChangeCallee("f1", "func1")
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

class ChangeCallee(ast.NodeTransformer):

    def __init__(self, oname:str, nname: str):
        self.oname = oname
        self.nname = nname

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.oname:
            result = copy.deepcopy(node)
            result.func.id = self.nname
            return result
        return node

class ReplaceVar(ast.NodeTransformer):

    def __init__(self):
        pass

    def visit_Name(self, node: ast.Name):
        pass

class NegateCond(ast.NodeTransformer):
    pass

class AddGuard(ast.NodeTransformer):
    pass

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