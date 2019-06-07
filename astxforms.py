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
    
    def code_motion(self, xf):
        assert xf.in_dim == len(self.ast.children)
        assert xf.name == "cm"

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
    out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

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
    xform.codegen(xf)
   
    xform.code_motion()
    
    print "Output Program"
    xform.codegen()

if __name__ == "__main__":
    cm_test()


        
