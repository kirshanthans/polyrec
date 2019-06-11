#!/usr/bin/python
import sys, os
from transformations import Transformation
from ast import *

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

        order = xf.out_ord        
        
        assert len(order) == len(self.mstmts)
        assert len(order) == len(self.mtynm)
        assert len(order) == len(self.mprms)
        
        funcs = [] #
        for ord_d, i in zip(order, xrange(len(order))):
            t = 'd' + str(i+1)
            stms = [self.mstmts[t]['g'+str(i+1)]]
            for l in ord_d[1:]:
                stms.append(self.mstmts[t][l])
            f = Function(self.mtynm[t][0], self.mtynm[t][1], self.mprms[t], stms)
            funcs.append(f)

        self.ast = Program(funcs)
        self.tag_map()

    def inter_change(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "ic"

    def inlining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "il"

    def strip_mining(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "sm"

    def codegen(self):
        return self.ast.codegen()

def cm_test():
    p = nest()
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
    
    xform = ASTXform(p)
    
    print "Input Program"
    print xform.codegen()
   
    xform.code_motion(xf)
    
    print "Output Program"
    print xform.codegen()

if __name__ == "__main__":
    cm_test()


        
