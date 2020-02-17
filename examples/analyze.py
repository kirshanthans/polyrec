import ast, astunparse, copy
from pprint import pprint

def test_change_callee(tree):
    analyzer = Analyzer()
    transformer = ChangeCallee("f1", "func1")
    analyzer.visit(transformer.visit(tree))
    analyzer.report()

def test_replace_var_linear(tree):
    analyzer = Analyzer()
    transformer = ReplaceVarLinear("i", 1)
    analyzer.visit(transformer.visit(tree))
    analyzer.report()

def test_replace_var_recursive(tree):
    analyzer = Analyzer()
    transformer = ReplaceVarRecursive("n", "l")
    analyzer.visit(transformer.visit(tree))
    analyzer.report()

def test_negate_cond(tree):
    analyzer = Analyzer()
    transformer = NegateCond()
    analyzer.visit(transformer.visit(tree))
    analyzer.report()

def test_add_guard(tree):
    analyzer = Analyzer()
    transformer = AddGuard()
    analyzer.visit(transformer.visit(tree))
    analyzer.report()

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions[node.name] = node
        #self.generic_visit(node)

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

class ReplaceVarLinear(ast.NodeTransformer):

    def __init__(self, vname: str, const: int):
        self.vname = vname
        self.const = const

    def visit_Name(self, node: ast.Name):
        if node.id == self.vname:
            result = ast.BinOp(left=ast.Name(self.vname, ctx=node.ctx), op=ast.Add(), right=ast.Num(self.const))
            return result
        return node

class ReplaceVarRecursive(ast.NodeTransformer):

    def __init__(self, vname: str, attr: str):
        self.vname = vname
        self.attr  = attr

    def visit_Name(self, node: ast.Name):
        if node.id == self.vname:
            result = ast.Attribute(value=ast.Name(self.vname, ctx=node.ctx), attr=self.attr, ctx=node.ctx)
            return result
        return node

class NegateCond(ast.NodeTransformer):

    def visit_If(self, node: ast.If):
        result = copy.deepcopy(node)
        cond   = copy.deepcopy(node.test)
        if isinstance(cond, ast.Compare):
            if len(cond.ops) == 1:
                if isinstance(cond.ops[0], ast.Eq):
                    cond.ops[0] = ast.NotEq()
                elif isinstance(cond.ops[0], ast.NotEq):
                    cond.ops[0] = ast.Eq()
        result.test = cond
        return result

class AddGuard(ast.NodeTransformer):

    def visit_Call(self, node: ast.Call):
        body = copy.deepcopy(node)
        result = ast.If(test=ast.NameConstant(True), body=[ast.Expr(body)], orelse=[])
        print(astunparse.unparse(result))
        return result

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
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        #print(ast.dump(tree))
        test_add_guard(tree)