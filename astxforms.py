#!/usr/bin/python
import sys, os
from transformations import Transformation
from ast import *

def change_callee(callexpr, callee):
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

def add_guardcond(cond, stmt):
    return IfStmt(cond, stmt, None)

def neg_cond(cond):
    return UnOp('~', cond)

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

    def code_motion(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "cm"

        out_ord = xf.out_ord        
        
        assert len(order) == len(self.mstmts)
        assert len(order) == len(self.mtynm)
        assert len(order) == len(self.mprms)
        
        funcs = [] 
        for ord_d, i in zip(out_ord, xrange(len(out_ord))):
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

        in_ord, out_ord = xf.in_ord, xf.out_ord

        funcs = [] 
        for ord_d, i in zip(out_ord, xrange(len(out_ord))):
            if i != dim and i != dim+1:
                t = 'd' + str(i+1)
                stms = [self.mstmts[t]['g'+str(i+1)]]
                for l in ord_d[1:]:
                    stms.append(self.mstmts[t][l])
                f = Function(self.mtynm[t][0], self.mtynm[t][1], self.mprms[t], stms)
                f.set_tag(t)
                funcs.append(f)
            
            elif i == dim:
                t1 = 'd' + str(i+1) 
                t2 = 'd' + str(i+2)
                guard = self.mstmts[t2]['g'+str(i+2)]
                guard.set_tag('g'+str(i+1))
                stms = [guard]
                for l in ord_d[1:]:
                    stm = None
                    if l[0] == 'r':
                        stm = change_callee(self.mstmts[t2]['r'+str(i+2)+l[2:]], self.mtynm[t1][1])
                    elif l[0] == 't' or l[0] == 's':
                        stm = self.mstmts[t1][l]
                    
                    assert stm != None
                    stm.set_tag(l)
                    stms.append(stm)
                
                f = Function(self.mtynm[t1][0], self.mtynm[t1][1], self.mprms[t1], stms)
                f.set_tag(t1)
                funcs.append(f)

            elif i == dim+1:
                t1 = 'd' + str(i) 
                t2 = 'd' + str(i+1)
                guard = self.mstmts[t1]['g'+str(i)]
                guard.set_tag('g'+str(i+1))
                stms = [guard]
                for l in ord_d[1:]:
                    stm = None
                    if l[0] == 'r':
                        stm = change_callee(self.mstmts[t1]['r'+str(i)+l[2:]], self.mtynm[t2][1])
                    elif l[0] == 't' or l[0] == 's':
                        stm = self.mstmts[t2][l]
                    
                    assert stm != None
                    stm.set_tag(l)
                    stms.append(stm)

                f = Function(self.mtynm[t2][0], self.mtynm[t2][1], self.mprms[t2], stms)
                f.set_tag(t2)
                funcs.append(f)
        
        self.ast = Program(funcs)
        self.tag_map()

    def inlining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "il"

        dim_inline  = xf.dim_inline
        call_inline = xf.call_inline
        label       = xf.label

        in_ord, out_ord = xf.in_ord, xf.out_ord

    def strip_mining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "sm"

    def codegen(self):
        return self.ast.codegen()

def cm_test():
    print "Code Motion Test"
    p = nest()
    xform = ASTXform(p)
    print "Input Program"
    print xform.codegen()
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
    
    xform.code_motion(xf)
    
    print "Output Program"
    print xform.codegen()

def ic_test():
    print "Interchange Test"
    p = nest()
    xform = ASTXform(p)
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
    
    print "Input Program"
    print xform.codegen()
   
    xform.inter_change(xf)
    
    print "Output Program"
    print xform.codegen()

def composition_test():
    print "Composition Test"
    p = nest()
    xform = ASTXform(p)
    print "Input Program"
    print xform.codegen()
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
    xform.code_motion(xf1)
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
    xform.inter_change(xf2)

    print "Output Program"
    print xform.codegen()

if __name__ == "__main__":
    composition_test()


        
