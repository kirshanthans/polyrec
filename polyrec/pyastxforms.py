import sys, os, copy
from polyrec.transformations import Transformation
from polyrec.pyast import Analyze
import ast, astunparse

class ReplaceVar(ast.NodeTransformer):
    def __init__(self, oname: str, nname: str):
        self.oname = oname
        self.nname = nname

    def visit_Name(self, node: ast.Name):
        if node.id == self.oname:
            result = copy.deepcopy(node)
            result.id = self.nname
            return result
        return node

class ChangeStride(ast.NodeTransformer):
    def __init__(self, stride: int):
        self.stride = stride

    def visit_BinOp(self, node: ast.BinOp):
        result = copy.deepcopy(node)
        if isinstance(node.right, ast.Num):
            result.right.n = self.stride
        return result

class CallAddArg(ast.NodeTransformer):
    def __init__(self, id, dim):
        self.dim = dim
        self.newarg = ast.Name(id=id, ctx=ast.Load())
    
    def visit_Call(self, node: ast.Call):
        result = copy.deepcopy(node)
        result.args.insert(self.dim, self.newarg)
        return result

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

def shift(d, dim):
    ret = {}
    for k in d:
        if k <= dim:
            ret[k] = d[k]
        else:
            ret[k+1] = d[k]
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
        
        #dim_inline  = xf.dim_inline
        #call_inline = xf.call_inline

        #in_ord, out_ord = xf.in_ord, xf.out_ord

    def strip_mining(self, xf):
        assert xf.in_dim == self.analyze.dims
        assert xf.name == "sm"

        strip_size = xf.strip_size
        dim_strip  = xf.dim_strip + 1 # 1 based indexing

        assert self.analyze.representation[dim_strip].loop

        #for k in self.analyze.indvars:
        #    print(ast.dump(self.analyze.indvars[k]))
        
        # add new induction variable
        dim_strip_indvar = self.analyze.indvars[dim_strip]
        new_dim_indvar = copy.deepcopy(dim_strip_indvar)
        new_dim_indvar.arg = new_dim_indvar.arg + str(dim_strip+1)

        self.analyze.indvars = shift(self.analyze.indvars, dim_strip)
        self.analyze.indvars[dim_strip+1] = new_dim_indvar
        
        # change induction variable order 
        new_indvar_id = self.analyze.indvars[dim_strip+1].arg
        addarg = CallAddArg(new_indvar_id, dim_strip)

        for d in range(1, self.analyze.dims+1):
            rep = self.analyze.representation[d]
            for r in rep.rcall:
                rep.rcall[r] = addarg.visit(rep.rcall[r])
            for t in rep.tcall:
                rep.tcall[t] = addarg.visit(rep.tcall[t])

        # shift dimension (first labels, then objects)
        for d in range(1, self.analyze.dims+1):
            if d > dim_strip:
                rep = self.analyze.representation[d]
                #print("before ", rep.dim)
                rep.dim += 1
                #print("after ", rep.dim)
                
                #print("before ", rep.alp)
                new_alp = ['e']
                for a in rep.alp[1:]:
                    if a[0] != 's':
                        new_alp.append(a[0]+str(rep.dim)+a[2:])
                    else:
                        new_alp.append(a)
                rep.alp = new_alp
                #print("after ", rep.alp)

                #print("before ", rep.ord)
                new_ord = ['e']
                for a in rep.ord[1:]:
                    if a[0] != 's':
                        new_ord.append(a[0]+str(rep.dim)+a[2:])
                    else:
                        new_ord.append(a)
                rep.ord = new_ord
                #print("after ", rep.ord)

                new_guard = {}
                for g in rep.guard:
                    new_guard[g[0]+str(rep.dim)+g[2:]] = rep.guard[g]
                rep.guard = new_guard

                new_rcall = {}
                for r in rep.rcall:
                    new_rcall[r[0]+str(rep.dim)+r[2:]] = rep.rcall[r]
                rep.rcall = new_rcall

                new_tcall = {}
                for t in rep.tcall:
                    new_tcall[t[0]+str(rep.dim)+t[2:]] = rep.tcall[t]
                rep.tcall = new_tcall

        new_reps = {}
        for d in range(1, self.analyze.dims+1):
            if d <= dim_strip:
                new_reps[d] = self.analyze.representation[d]
            else:
                new_reps[d+1] = self.analyze.representation[d]
        
        self.analyze.representation = new_reps
        
        # set dims
        self.analyze.dims += 1

        # construct new dimension
        self.analyze.representation[dim_strip+1] = copy.deepcopy(self.analyze.representation[dim_strip])
        self.analyze.representation[dim_strip+1].fname += str(dim_strip+1)
        # change call names in new dim
        strip_dim_name = self.analyze.representation[dim_strip].fname
        new_dim_name = self.analyze.representation[dim_strip+1].fname
        changercall = ChangeCallee(strip_dim_name, new_dim_name)

        for r in self.analyze.representation[dim_strip+1].rcall:
            self.analyze.representation[dim_strip+1].rcall[r] = changercall.visit(self.analyze.representation[dim_strip+1].rcall[r])

        # change tcall in dim_strip
        if dim_strip+1 < self.analyze.dims:
            old_tcall_name = self.analyze.representation[dim_strip+2].fname
            new_tcall_name = self.analyze.representation[dim_strip+1].fname
            changetcall = ChangeCallee(old_tcall_name, new_tcall_name)

            for t in self.analyze.representation[dim_strip].tcall:
                self.analyze.representation[dim_strip].tcall[t] = changetcall.visit(self.analyze.representation[dim_strip].tcall[t])
        else:
            # last dimension strip mining must be handled separately
            pass
        # fix stride in dim_strip
        changestride = ChangeStride(strip_size)
        for r in self.analyze.representation[dim_strip].rcall:
            self.analyze.representation[dim_strip].rcall[r].args[dim_strip-1] = changestride.visit(self.analyze.representation[dim_strip].rcall[r].args[dim_strip-1])


        indvar_labels = self.analyze.getindvar()
        for r in self.analyze.representation[dim_strip+1].rcall:
            call = self.analyze.representation[dim_strip+1].rcall[r]
            call.args[dim_strip-1] = ast.Name(id=indvar_labels[dim_strip-1], ctx=ast.Load())
            call.args[dim_strip] = ast.BinOp(left=ast.Name(id=indvar_labels[dim_strip], ctx=ast.Load()),
                                             op=ast.Add(),
                                             right=ast.Num(n=1))
        
        # if new dimension has work
        if self.analyze.representation[dim_strip+1].work != {}:
            pass
            oname = indvar_labels[dim_strip-1]
            nname = indvar_labels[dim_strip]
            changename = ReplaceVar(oname, nname)
            for s in self.analyze.representation[dim_strip+1].work:
                self.analyze.representation[dim_strip+1].work[s] = changename.visit(self.analyze.representation[dim_strip+1].work[s])

        #if following dimension has work
        if dim_strip+1 < self.analyze.dims:
            if self.analyze.representation[dim_strip+2].work != {}:
                oname = indvar_labels[dim_strip-1]
                nname = indvar_labels[dim_strip]
                changename = ReplaceVar(oname, nname)
                for s in self.analyze.representation[dim_strip+2].work:
                    self.analyze.representation[dim_strip+2].work[s] = changename.visit(self.analyze.representation[dim_strip+2].work[s])


        # fix bounds in dim_strip+1
        indvar_new_dim = indvar_labels[dim_strip]
        newbound = ast.Compare(left=ast.Name(id=indvar_new_dim, ctx=ast.Load()),
                               ops=[ast.GtE()],
                               comparators=[ast.Num(n=strip_size)])
        oguard = self.analyze.representation[dim_strip].guard['g'+str(dim_strip)]
        nguard = ast.BoolOp(op=ast.Or(),
                            values=[oguard, newbound])
        self.analyze.representation[dim_strip+1].guard['g'+str(dim_strip)] = nguard # labels are not fixed yet

        # fix labels for new dimension
        rep = self.analyze.representation[dim_strip+1]
        #print("before ", rep.dim)
        rep.dim += 1
        #print("after ", rep.dim)
        
        #print("before ", rep.alp)
        new_alp = ['e']
        for a in rep.alp[1:]:
            if a[0] != 's':
                new_alp.append(a[0]+str(rep.dim)+a[2:])
            else:
                new_alp.append(a)
        rep.alp = new_alp
        #print("after ", rep.alp)

        #print("before ", rep.ord)
        new_ord = ['e']
        for a in rep.ord[1:]:
            if a[0] != 's':
                new_ord.append(a[0]+str(rep.dim)+a[2:])
            else:
                new_ord.append(a)
        rep.ord = new_ord
        #print("after ", rep.ord)

        new_guard = {}
        for g in rep.guard:
            new_guard[g[0]+str(rep.dim)+g[2:]] = rep.guard[g]
        rep.guard = new_guard


        new_rcall = {}
        for r in rep.rcall:
            new_rcall[r[0]+str(rep.dim)+r[2:]] = rep.rcall[r]
        rep.rcall = new_rcall

        new_tcall = {}
        for t in rep.tcall:
            new_tcall[t[0]+str(rep.dim)+t[2:]] = rep.tcall[t]
        rep.tcall = new_tcall

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

def sm_test():
    print("Strip Mining Test")
    with open("examples/sources/loop-rec.py", "r") as source:
        tree = ast.parse(source.read())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim + 1
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # strip dimension
        strip_dim = 0
        # strip size
        strip_size = 2
        # Transform
        xf = Transformation(
            name        = 'sm',
            in_dim      = in_dim, 
            out_dim     = out_dim, 
            in_dim_type = in_dim_type, 
            in_alp      = in_alp, 
            in_ord      = in_ord, 
            dim_strip   = strip_dim, 
            strip_size  = strip_size)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def composition_test():
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
        
        # code-motion 
        out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]
        
        xf1 = Transformation(
            name         ='cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)
        xform.transform(xf1)

        # interchange
        dim1 = 0
        dim2 = 1

        xf2 = Transformation(
            name         ='ic',
            in_dim       = xf1.out_dim,
            out_dim      = xf1.out_dim,
            in_dim_type  = xf1.out_dim_type,
            in_alp       = xf1.out_alp,
            in_ord       = xf1.out_ord,
            dim_i1       = dim1,
            dim_i2       = dim2)
        xform.transform(xf2)
        
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

if __name__ == "__main__":
    cm_test()
    ic_test()
    sm_test()
    composition_test()