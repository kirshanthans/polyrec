import ast, astunparse

class AnalyzeSelfCall(ast.NodeVisitor):

    def __init__(self, fname: str):
        self.fname = fname
        self.rcall = 0

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.fname:
            self.rcall += 1
        
class AnalyzeInductionVar(ast.NodeVisitor):

    def __init__(self, tags: list):
        self.tags = tags
        self.indvars = {}

    def visit_arguments(self, node: ast.arguments):
        assert len(self.tags) == len(node.args)
        self.indvars = dict(zip(self.tags, node.args))

class AnalyzeFunctionOrder(ast.NodeVisitor):

    def __init__(self, dim: int, fname: str, loop: bool):
        self.dim   = dim
        self.fname = fname
        self.loop  = loop
        self.alp   = ['e']
        self.ord   = ['e']
        self.guard = None
        self.rcall = {}
        self.tcall = None
        self.work  = None

    def visit_If(self, node: ast.If):
        if isinstance(node.body[0], ast.Return):
            self.guard = node.test

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.fname:
            if self.loop:
                label = "r"+str(self.dim) 
                self.ord.append(label)
                self.rcall[label] = node
            else:
                if isinstance(node.args[self.dim-1], ast.Attribute):
                    label = "r"+str(self.dim)+node.args[self.dim-1].attr
                    self.ord.append(label)
                    self.rcall[label] = node
        else:
            label = "t"+str(self.dim) 
            self.ord.append(label)
            self.tcall = node

    def visit_Assign(self, node: ast.Assign):
        self.ord.append("s1")
        self.work = node

    def set_alp(self):
        rec = []
        trs = []

        for s in self.ord:
            if s[0] == 'r':
                rec.append(s)
            elif s[0] == 't' or s[0] == 's':
                trs.append(s)

        self.alp = self.alp + rec + trs

class AnalyzeCollection(ast.NodeVisitor):
    
    def __init__(self):
        self.functions = {}
        self.dims = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.dims += 1
        self.functions[self.dims] = node

class Analyze:

    def __init__(self, tree):
        self.tree = tree
        self.dims = 0
        self.functions = {}
        self.indvars = {}
        self.representation = {}

    def collect(self):
        collectionWalk = AnalyzeCollection()
        collectionWalk.visit(self.tree)
        self.dims = collectionWalk.dims
        self.functions = collectionWalk.functions
        
        for i in range(1, self.dims+1):
            self.func(i, self.functions[i])
        
        indvarWalk = AnalyzeInductionVar(range(1, self.dims+1))
        indvarWalk.visit(self.functions[1])
        self.indvars = indvarWalk.indvars

    def func(self, dim: int, node: ast.FunctionDef):
        rcallWalk = AnalyzeSelfCall(node.name)
        rcallWalk.visit(node)
        
        loop = (rcallWalk.rcall == 1)
        funcOrdWalk = AnalyzeFunctionOrder(dim, node.name, loop)
        funcOrdWalk.visit(node)
        funcOrdWalk.set_alp()
        self.representation[dim] = funcOrdWalk

    def getdim(self):
        return self.dims

    def getdimtype(self):
        dim = self.dims
        dim_type = []

        for f in range(1, dim+1):
            dim_type.append(len(self.representation[f].rcall))

        return dim_type
    
    def getord(self):
        dim = self.dims
        order = []
        
        for f in range(1, dim+1):
            order.append(self.representation[f].ord)

        return order

    def getalp(self):
        dim = self.dims
        alph = []
        
        for f in range(1, dim+1):
            alph.append(self.representation[f].alp)

        return alph

    def getindvar(self):
        dim = self.dims
        indvar = []

        for f in range(1, dim+1):
            indvar.append(self.indvars[f].arg)

        return indvar

if __name__ == "__main__":
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        #print(ast.dump(tree))
        print(astunparse.unparse(tree))
        analyze = Analyze(tree)
        analyze.collect()
        print(analyze.getdim())
        print(analyze.getdimtype())
        print(analyze.getalp())
        print(analyze.getord())
        print(analyze.getindvar())
