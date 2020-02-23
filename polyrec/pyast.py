import ast, astunparse, copy
from polyrec.witnesstuples import WitnessTuple

class AnalyzeTreeReads(ast.NodeVisitor):
    def __init__(self):
        self.treereads = set([])
    def visit_Attribute(self, node: ast.Attribute):
        if node.attr == 'l' or node.attr == 'r':
            self.treereads.add(node.attr)
        self.generic_visit(node)

class AnalyzeArrayReads(ast.NodeVisitor):
    def __init__(self):
        self.arrayreads = set([])
    
    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, ast.BinOp):
                if isinstance(node.slice.value.op, ast.Add):
                    self.arrayreads.add(node.slice.value.right.n)
                elif isinstance(node.slice.value.op, ast.Sub):
                    self.arrayreads.add(-node.slice.value.right.n)
            if isinstance(node.slice.value, ast.Name):
                self.arrayreads.add(0)

class AnalyzeTreeWrites(ast.NodeVisitor):
    def __init__(self):
        self.treewrites = set([])

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr == 'l' or node.attr == 'r':
            self.treewrites.add(node.attr)
        self.generic_visit(node)

class AnalyzeArrayWrites(ast.NodeVisitor):
    def __init__(self):
        self.arraywrites = set([])

    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, ast.BinOp):
                if isinstance(node.slice.value.op, ast.Add):
                    self.arraywrites.add(node.slice.value.right.n)
                elif isinstance(node.slice.value.op, ast.Sub):
                    self.arraywrites.add(-node.slice.value.right.n)
            if isinstance(node.slice.value, ast.Name):
                self.arraywrites.add(0)

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

    def constructf(self):
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

    def cgen(self):
        body = []
        bound = astunparse.unparse(self.guard['g'+str(self.dim)]).strip().replace('or', '||').rstrip()
        termination = "if " + bound + "{\nreturn;\n}"
        body.append(termination)

        for label in self.ord[1:]:
            if label[0] == "t":
                s = astunparse.unparse(ast.Expr(self.tcall[label])).rstrip()
                s += ';'
                body.append(s)
            elif label[0] == "r":
                s = astunparse.unparse(ast.Expr(self.rcall[label])).rstrip()
                s += ';'
                body.append(s)
            else:
                s = astunparse.unparse(ast.Expr(self.work[label])).replace('.', '->').rstrip()
                s += ';'
                body.append(s)
        
        return body

class Analyze:

    def __init__(self, tree):
        self.tree = tree         # module tree
        self.dims = 0            # dimensions
        self.indvars = {}        # induction variables
        self.representation = {} # map: dimension -> function reps
        self.deps = set([])

    def collect(self):
        collectionWalk = AnalyzeCollection()
        collectionWalk.visit(self.tree)
        self.dims = collectionWalk.dims
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

    def constructfs(self):
        dims = self.dims
        args = []
        for d in range(1, self.dims+1):
            args.append(self.indvars[d])
        fs = []
        for t in range(1, dims+1):
            fnode = self.representation[t].constructf()
            fnode.args = ast.arguments(args=args, vararg=None, 
                                       kwonlyargs=[], kw_defaults=[], 
                                       kwarg=None, defaults=[])
            fs.append(fnode)
        
        return fs
            
    def codegen(self):
        s = ""
        for f in self.constructfs():
            s += astunparse.unparse(f)
        return s

    def cgen(self):
        dims = self.dims
        
        args = self.getindvar()
        s_arg = []
        for d, arg in enumerate(args):
            if self.representation[d+1].loop:
                s_arg.append("int " + arg)
            else:
                s_arg.append("Node * " + arg)

        ss_arg = s_arg[0] 
        for s in s_arg[1:]:
            ss_arg += ", " + s  

        s = ''
        for d in range(1, dims+1):
            sfunc = "void " + self.representation[d].fname + "(" + ss_arg + "){\n"
            
            stmts = self.representation[d].cgen()
            for st in stmts:
                sfunc += "" + st + "\n"
            sfunc += "}\n\n"
            s += sfunc

        return s
    
    def depanalyze(self):
        dims = self.dims
        stmt = self.representation[dims].work['s1']
        # print(ast.dump(stmt))
        # Reads
        treads = AnalyzeTreeReads()
        areads = AnalyzeArrayReads()
        treads.visit(stmt.value)
        areads.visit(stmt.value)
        # Writes
        twrites  = AnalyzeTreeWrites()
        awrites = AnalyzeArrayWrites()
        for t in stmt.targets:
            twrites.visit(t)
            awrites.visit(t)

        #print("read array: ", areads.arrayreads)
        #print("read tree: ", treads.treereads)
        #print("write array: ", awrites.arraywrites)
        #print("write tree: ", twrites.treewrites)

        for x in areads.arrayreads:
            if x != 0 and x > 0:
                rgx1 = [['t1'],['s1']]
                rgx2 = [['t1'],['s1']]
                
                if 0 in areads.arrayreads and 0 in awrites.arraywrites:
                    rgx2[0].insert(0, '(r1)*')
                
                for _ in range(x):
                   rgx2[0].insert(0, 'r1') 
                wt = WitnessTuple(self.getdim(), self.getdimtype(), self.getalp(), self.getord(), rgx1, rgx2)
                wt.set_fsa()
                self.deps.add(wt)

        for l in treads.treereads:
            rgx1 = [['t1'],['s1']]
            rgx2 = [['t1'],['s1']]
            for r in self.representation[2].rcall:
                if r[2:] == l:
                    if self.representation[2].ord.index(r) < self.representation[2].ord.index('s1'):
                        rgx1[1].insert(0, r)
                    else:
                        rgx2[1].insert(0, r)
                    wt = WitnessTuple(self.getdim(), self.getdimtype(), self.getalp(), self.getord(), rgx1, rgx2)
                    wt.set_fsa()
                    self.deps.add(wt)

    def getdeps(self):
        ret = []
        for i, dep in enumerate(self.deps):
            ret.append((i, dep.regex1, dep.regex2))
        return ret

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
        print(analyze.codegen())
        #print(analyze.cgen())
        analyze.depanalyze()
        print(analyze.getdeps())
