import sys, os, copy
from polyrec.transformations import Transformation
from polyrec.pyast import Analyze
import ast, astunparse

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

class InterchangeArg(ast.NodeTransformer):

    def __init__(self, pos1: int, pos2: int):
        self.pos1 = pos1
        self.pos2 = pos2

    def visit_Call(self, node: ast.Call):
        result = copy.deepcopy(node)
        result.args[self.pos1], result.args[self.pos2] = result.args[self.pos2], result.args[self.pos1] 
        return result

def cleanup(d, new_dim):
    ret = {}
    for k in d:
        ret[k[0]+str(new_dim)+k[2:]] = d[k]
    return ret

class Transform:
    def __init__(self, analyze):
        self.analyze = analyze
        self.analyze.collect()
    
    def transform(self, xf):
        if xf.name == "cm":
            self.code_motion(xf)
        elif xf.name == "ic":
            self.inter_change(xf)
        elif xf.name == "il":
            self.inlining(xf)
        elif xf.name == "sm":
            self.strip_mining(xf)
        else:
            assert False    
    
    def code_motion(self, xf):
        assert xf.in_dim == self.analyze.dims
        assert xf.name == "cm"

        out_ord = xf.out_ord        
        
        dims = self.analyze.dims
        for t in range(1, dims+1):
            self.analyze.representation[t].ord = out_ord[t-1]

    def inter_change(self, xf):
        assert xf.in_dim == self.analyze.dims
        assert xf.name == "ic"

        dim = xf.dim_i1
        t1 = dim+1
        t2 = dim+2

        out_alp = xf.out_alp
        out_ord = xf.out_ord
        
        self.analyze.indvars[t1], self.analyze.indvars[t2] = self.analyze.indvars[t2], self.analyze.indvars[t1]

        rep1 = self.analyze.representation[t1]
        rep2 = self.analyze.representation[t2]

        rep1.loop, rep2.loop = rep2.loop, rep1.loop
        rep1.alp, rep2.alp = out_alp[t1-1], out_alp[t2-1]
        rep1.ord, rep2.ord = out_ord[t1-1], out_ord[t2-1]
        
        rep1.guard['g'+str(t1)], rep2.guard['g'+str(t2)] = rep2.guard['g'+str(t2)], rep1.guard['g'+str(t1)]
        rcall_1, rcall_2 = rep2.rcall, rep1.rcall
        rcall_1 = cleanup(rcall_1, t1)
        rcall_2 = cleanup(rcall_2, t2)
        rep1.rcall, rep2.rcall = rcall_1, rcall_2

        argChange = InterchangeArg(t1-1, t2-1)
        calleeChange1 = ChangeCallee(rep1.fname, rep2.fname)
        calleeChange2 = ChangeCallee(rep2.fname, rep1.fname)
        for k in rep1.tcall:
            rep1.tcall[k] = argChange.visit(rep1.tcall[k])
        for k in rep2.tcall:
            rep2.tcall[k] = argChange.visit(rep2.tcall[k])
        for k in rep1.rcall:
            rep1.rcall[k] = argChange.visit(rep1.rcall[k])
            rep1.rcall[k] = calleeChange2.visit(rep1.rcall[k])
        for k in rep2.rcall:
            rep2.rcall[k] = argChange.visit(rep2.rcall[k])
            rep2.rcall[k] = calleeChange1.visit(rep2.rcall[k])

    def inlining(self, xf):
        assert xf.in_dim == self.analyze.dims
        assert xf.name == "il"
        pass

    def strip_mining(self, xf):
        assert xf.in_dim == self.analyze.dims
        assert xf.name == "sm"
        pass

    def codegen(self):
        s = ""
        for f in self.analyze.codegen():
            s += astunparse.unparse(f)
        return s

def cm_test():
    print("Code Motion Test")
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # Output order
        out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]
        # Transform
        xf = Transformation(
            name         ='cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def ic_test():
    print("Interchange Test")
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # Transform
        xf = Transformation(
            name         ='ic',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            dim_i1       = 0,
            dim_i2       = 1)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def composition_test():
    pass

if __name__ == "__main__":
    composition_test()