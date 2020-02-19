import ast, astunparse, copy

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
        self.indvars = dict(zip(self.tags, copy.deepcopy(node.args)))

class AnalyzeCollection(ast.NodeVisitor):
    
    def __init__(self):
        self.functions = {}
        self.dims = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.dims += 1
        self.functions[self.dims] = node

class AnalyzeFunction(ast.NodeVisitor):

    def __init__(self, dim: int, fname: str, loop: bool):
        self.dim   = dim
        self.fname = fname
        self.loop  = loop # true or false
        self.alp   = ['e']
        self.ord   = ['e']
        self.guard = {}   # label: g<dim>
        self.rcall = {}   # label: r<dim><label>
        self.tcall = {}   # label: t<dim>
        self.work  = {}   # label: s1

    def visit_If(self, node: ast.If):
        if isinstance(node.body[0], ast.Return):
            self.guard['g'+str(self.dim)] = copy.deepcopy(node.test)

    def visit_Call(self, node: ast.Call):
        if node.func.id == self.fname:
            if self.loop:
                label = "r"+str(self.dim) 
                self.ord.append(label)
                self.rcall[label] = copy.deepcopy(node)
            else:
                if isinstance(node.args[self.dim-1], ast.Attribute):
                    label = "r"+str(self.dim)+node.args[self.dim-1].attr
                    self.ord.append(label)
                    self.rcall[label] = copy.deepcopy(node)
        else:
            label = "t"+str(self.dim) 
            self.ord.append(label)
            self.tcall[label] = copy.deepcopy(node)

    def visit_Assign(self, node: ast.Assign):
        self.ord.append('s1')
        self.work['s1'] = copy.deepcopy(node)

    def set_alp(self):
        rec = []
        trs = []

        for s in self.ord:
            if s[0] == 'r':
                rec.append(s)
            elif s[0] == 't' or s[0] == 's':
                trs.append(s)

        self.alp = self.alp + rec + trs

    def codegen(self):
        ret_node = ast.FunctionDef(name=self.fname, args=[], 
                                   decorator_list=[], returns=ast.NameConstant(None))
        body_node = [ast.If(test=copy.deepcopy(self.guard['g'+str(self.dim)]), 
                           body=[ast.Return(None)], orelse=[])]

        for label in self.ord[1:]:
            if label[0] == "t":
                body_node.append(ast.Expr(copy.deepcopy(self.tcall[label])))
            elif label[0] == "r":
                body_node.append(ast.Expr(copy.deepcopy(self.rcall[label])))
            else:
                body_node.append(copy.deepcopy(self.work[label]))

        ret_node.body = body_node
        return ret_node

class Analyze:

    def __init__(self, tree):
        self.tree = tree # module tree
        self.dims = 0
        #self.functions = {} # only to keep the original function trees
        self.indvars = {}
        self.representation = {} # map for analyze function order objects

    def collect(self):
        collectionWalk = AnalyzeCollection()
        collectionWalk.visit(self.tree)
        self.dims = collectionWalk.dims
        #self.functions = collectionWalk.functions
        functions = collectionWalk.functions
        
        indvarWalk = AnalyzeInductionVar(range(1, self.dims+1))
        indvarWalk.visit(functions[1])
        self.indvars = indvarWalk.indvars
        
        for i in range(1, self.dims+1):
            self.func(i, functions[i])

    def func(self, dim: int, node: ast.FunctionDef):
        rcallWalk = AnalyzeSelfCall(node.name)
        rcallWalk.visit(node)
        loop = (rcallWalk.rcall == 1)

        funcWalk = AnalyzeFunction(dim, node.name, loop)
        funcWalk.visit(node)
        funcWalk.set_alp()
        self.representation[dim] = funcWalk

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

    def codegen(self):
        dims = self.dims
        args = list(self.indvars.values())
        fs = []
        for t in range(1, dims+1):
            fnode = self.representation[t].codegen()
            fnode.args = ast.arguments(args=args, vararg=None, 
                                       kwonlyargs=[], kw_defaults=[], 
                                       kwarg=None, defaults=[])
            fs.append(fnode)
        
        return fs
            


if __name__ == "__main__":
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        analyze = Analyze(tree)
        analyze.collect()
        print(analyze.getdim())
        print(analyze.getdimtype())
        print(analyze.getalp())
        print(analyze.getord())
        print(analyze.getindvar())
        for f in analyze.codegen():
            print(astunparse.unparse(f))
