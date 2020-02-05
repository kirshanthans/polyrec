import sys, os
from polyrec.transformations import Transformation
from polyrec.ast import nest, Program, Function, CallExpr, IfStmt, ReturnStmt, Assignment, BinOp, UnOp, Array, Field, Number, Const, Var

def switch_tags(nodes, t1, t2):
    if isinstance(nodes, list):
        for n in nodes:
            if n.tag == t1:
                n.set_tag(t2)
            elif n.tag == t2:
                n.set_tag(t1)
    else:
        if nodes.tag == t1:
            nodes.set_tag(t2)
        elif nodes.tag == t2:
            nodes.set_tag(t1)

def change_callee(callexpr, callee, t1, t2):
    switch_tags(callexpr.args, t1, t2)
    return CallExpr(callee, callexpr.args)

def replace_var(node, var, binop):
    if isinstance(node, IfStmt):
        return IfStmt(replace_var(node.cond, var, binop), 
                      replace_var(node.then, var, binop), 
                      replace_var(node.els, var, binop))
    elif isinstance(node, ReturnStmt):
        return ReturnStmt(replace_var(node.expr, var, binop))
    elif isinstance(node, Assignment):
        return Assignment(replace_var(node.lhs, var, binop),
                          replace_var(node.rhs, var, binop))
    elif isinstance(node, CallExpr):
        return CallExpr(node.callee, [replace_var(c, var, binop) for c in node.args])
    elif isinstance(node, BinOp):
        return BinOp(node.op, 
                     replace_var(node.lhs, var, binop), 
                     replace_var(node.rhs, var, binop))
    elif isinstance(node, Array):
        return Array(replace_var(node.var, var, binop), 
                     replace_var(node.index, var, binop))
    elif isinstance(node, Field):
        return Field(node.label)
    elif isinstance(node, Number):
        return Number(node.value)
    elif isinstance(node, Const):
        return Const(node.value)
    elif isinstance(node, Var):
        if node == var:
            return binop
        else:
            return Var(node.name)

def neg_cond(cond):
    return UnOp('~', cond)

def add_guardcond(cond, stmt):
    return IfStmt(neg_cond(cond), stmt, None)

def inline_stmt(cond, binop, var, stmt):
    return add_guardcond(cond, replace_var(stmt, var, binop))

class ASTXform:
    def __init__(self, ast):
        self.ast = ast
        self.mstmts = {} # map of a map key: tag val: map -> (label, stmt)
        self.mtynm  = {} # map of name type key: tag val: (type, name)
        self.mprms  = {} # map of parameters key: tag val: [params]
        self.tag_map()
    
    def tag_map(self):
        # initialization
        self.mstmts = {} 
        self.mtynm  = {} 
        self.mprms  = {} 
        
        funcs = self.ast.children # get all the functions in the nest
        for f in funcs:
            t = f.tag # create a map for each function
            
            self.mtynm[t] = (f.typ, f.name) # type and name
            self.mprms[t] = f.params # parameters
            
            m = {}
            for st in f.children:
                m[st.tag] = st # add all statements to the corresponding function map
            self.mstmts[t] = m

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
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "cm"

        out_ord = xf.out_ord        
        
        assert len(out_ord) == len(self.mstmts)
        assert len(out_ord) == len(self.mtynm)
        assert len(out_ord) == len(self.mprms)
        
        funcs = [] 
        for ord_d, i in zip(out_ord, range(len(out_ord))):
            t = 'd' + str(i+1)
            stms = [self.mstmts[t]['g'+str(i+1)]]
            for l in ord_d[1:]:
                stms.append(self.mstmts[t][l])
            f = Function(self.mtynm[t][0], self.mtynm[t][1], self.mprms[t], stms)
            f.set_tag(t)
            funcs.append(f)

        self.ast = Program(funcs)
        self.tag_map()

    def inter_change(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "ic"

        dim = xf.dim_i1
        t1 = 'd' + str(dim+1) 
        t2 = 'd' + str(dim+2)

        out_ord = xf.out_ord

        funcs = [] 
        for ord_d, i in zip(out_ord, range(len(out_ord))):
            if i != dim and i != dim+1:
                t = 'd' + str(i+1)
                stms = [self.mstmts[t]['g'+str(i+1)]]
                for l in ord_d[1:]:
                    if l[0] == 'r' or l[0] == 't':
                        stms.append(change_callee(self.mstmts[t][l], self.mstmts[t][l].callee, t1, t2))
                    else:
                        stms.append(self.mstmts[t][l])
                
                switch_tags(self.mprms[t], t1, t2)
                f = Function(self.mtynm[t][0], self.mtynm[t][1], self.mprms[t], stms)
                f.set_tag(t)
                funcs.append(f)
            
            elif i == dim:
                guard = self.mstmts[t2]['g'+str(i+2)]
                guard.set_tag('g'+str(i+1))
                stms = [guard]
                for l in ord_d[1:]:
                    stm = None
                    if l[0] == 'r':
                        stm = change_callee(self.mstmts[t2]['r'+str(i+2)+l[2:]], self.mtynm[t1][1], t1, t2)
                    elif l[0] == 't':
                        stm = change_callee(self.mstmts[t1][l], self.mstmts[t1][l].callee, t1, t2)
                    elif l[0] == 's':
                        stm = self.mstmts[t1][l]
                    
                    assert stm != None
                    stm.set_tag(l)
                    stms.append(stm)
                
                switch_tags(self.mprms[t1], t1, t2)
                f = Function(self.mtynm[t1][0], self.mtynm[t1][1], self.mprms[t1], stms)
                f.set_tag(t1)
                funcs.append(f)

            elif i == dim+1:
                guard = self.mstmts[t1]['g'+str(i)]
                guard.set_tag('g'+str(i+1))
                stms = [guard]
                for l in ord_d[1:]:
                    stm = None
                    if l[0] == 'r':
                        stm = change_callee(self.mstmts[t1]['r'+str(i)+l[2:]], self.mtynm[t2][1], t1, t2)
                    elif l[0] == 't':
                        stm = change_callee(self.mstmts[t2][l], self.mstmts[t2][l].callee, t1, t2)
                    elif l[0] == 's':
                        stm = self.mstmts[t2][l]
                    
                    assert stm != None
                    stm.set_tag(l)
                    stms.append(stm)

                switch_tags(self.mprms[t2], t1, t2)
                f = Function(self.mtynm[t2][0], self.mtynm[t2][1], self.mprms[t2], stms)
                f.set_tag(t2)
                funcs.append(f)


        self.ast = Program(funcs)
        self.tag_map()

    def inlining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "il"

        dim_inline  = xf.dim_inline # dimension to inline
        call_inline = xf.call_inline # call to inline

        call_label = xf.in_alp[dim_inline][call_inline]

        in_ord, out_ord = xf.in_ord, xf.out_ord

        funcs = [] 
        for ord_d, i in zip(out_ord, range(len(out_ord))):
            t = 'd' + str(i+1)
            guard = self.mstmts[t]['g'+str(i+1)]
            stms = [guard]
            
            if i != dim_inline: # copying the other dimensions as it is
                for l in ord_d[1:]:
                    stms.append(self.mstmts[t][l])
            else:
                in_ord_d = in_ord[i] # input order of the inlining dimension
                for l, pos in zip(in_ord_d, range(len(in_ord_d))):
                    if pos == 0: # escaping the empty symbol in the order
                        continue
                    if l != call_label: # copying statements that are non inlined as it is
                        stms.append(self.mstmts[t][l])
                    else:
                        in_call_stm = self.mstmts[t][l] # call expr that is getting inlined
                        ind_binop = None # Find the corresponding index var change to the inlining call expr 
                        for a in in_call_stm.args:
                            if a.tag == t:
                                ind_binop = a
                        
                        ind_var = None # Find the corresponding index var for the dimension
                        for p in self.mprms[t]:
                            if p.tag == t:
                                ind_var = p.var

                        assert ind_binop != None
                        assert ind_var != None

                        inline_stms = []
                        inline_labl = ord_d[pos:pos+len(in_ord_d[1:])] # getting the output labels

                        in_stmts = []
                        for inl in in_ord_d[1:]: # taking all the stmts in the input function body
                            in_stmts.append(self.mstmts[t][inl])

                        assert len(inline_labl) == len(in_stmts)

                        for inl,inst in zip(inline_labl, in_stmts): # constructing the inlined stmts
                            in_stm = inline_stmt(guard.cond, ind_binop, ind_var, inst)
                            in_stm.set_tag(inl)
                            inline_stms.append(in_stm)

                        for st in inline_stms: # adding the inlined stmts to output function body
                            stms.append(st)
            
            f = Function(self.mtynm[t][0], self.mtynm[t][1], self.mprms[t], stms)
            f.set_tag(t)
            funcs.append(f)
        
        self.ast = Program(funcs)
        self.tag_map()

    def strip_mining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "sm"
        pass

    def codegen(self):
        return self.ast.codegen()

def cm_test():
    print("Code Motion Test")
    p = nest()
    xform = ASTXform(p)
    print("Input Program")
    print(xform.codegen())
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # Output order
    out_ord = [['e', 'r1', 't1'], ['e', 's1', 'r2l', 'r2r']]

    xf = Transformation(
        name         ='cm',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        out_ord      = out_ord)
    xform.transform(xf)
    
    print("Output Program")
    print(xform.codegen())

def ic_test():
    print("Interchange Test")
    p = nest()
    xform = ASTXform(p)
    print("Input Program")
    print(xform.codegen())
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

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
    
    print("Output Program")
    print(xform.codegen())

def il_test():
    print("Code Motion Test")
    p = nest()
    xform = ASTXform(p)
    print("Input Program")
    print(xform.codegen())   
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    xf = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 1,
        call_inline = 1,
        label       = 'l')
    xform.transform(xf)
    
    print("Output Program")
    print(xform.codegen())

def sm_test():
    print("Strip Mining Test")
    p = nest()
    xform = ASTXform(p)    
    print("Input Program")
    print(xform.codegen())
    # Dimensions
    in_dim  = 2
    out_dim = 3
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # strip dimension 
    strip_dim  = 0
    # strip size
    strip_size = 2

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
    
    print("Output Program")
    print(xform.codegen())

def composition_test():
    print("Composition Test")
    p = nest()
    xform = ASTXform(p)
    print("Input Program")
    print(xform.codegen())
    # Dimensions
    dim  = 2
    # Type of dimensions
    dim_type = [1, 2]

    # code-motion 
    alp1  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    ord2  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    xf1 = Transformation(
        name         = 'cm',
        in_dim       = dim,
        out_dim      = dim,
        in_dim_type  = dim_type,
        in_alp       = alp1,
        in_ord       = ord1,
        out_ord      = ord2)
    xform.transform(xf1)
    
    # Interchange
    dim1_ = 0
    dim2_ = 1
    
    xf2 = Transformation(
        name         ='ic',
        in_dim       = xf1.out_dim,
        out_dim      = xf1.out_dim,
        in_dim_type  = xf1.out_dim_type,
        in_alp       = xf1.out_alp,
        in_ord       = xf1.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)
    xform.transform(xf2)
    
    # Inline
    dim_il   = 1
    call_il  = 1
    label_il = 'n'
    
    xf3 = Transformation(
        name        = 'il',
        in_dim      = xf2.out_dim,
        out_dim     = xf2.out_dim,
        in_dim_type = xf2.out_dim_type,
        in_alp      = xf2.out_alp,
        in_ord      = xf2.out_ord,
        dim_inline  = dim_il,
        call_inline = call_il,
        label       = label_il)
    xform.transform(xf3)
    
    print("Output Program")
    print(xform.codegen())

if __name__ == "__main__":
    composition_test()


        
