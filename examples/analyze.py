import ast
from pprint import pprint
def main():
    with open("examples/py_files/test.py", "r") as source:
        tree = ast.parse(source.read())
        print(ast.dump(tree))
        analyzer = Analyzer()
        analyzer.visit(tree)
        analyzer.report()

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"functions":[]}

    def visit_FunctionDef(self, node):
        self.stats["functions"].append(node)
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)

if __name__ == "__main__":
    main()