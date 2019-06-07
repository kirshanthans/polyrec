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
    
    def code_motion(self, out_ord):
        pass

    def inter_change(self, dim1, dim2):
        pass

    def inlining(self, dim, call, label):
        pass

    def strip_mining(self, dim, size):
        pass

    def codegen(self):
        
        return self.ast.codegen()

def cm_test():
    ast = None 
    
    xform = ASTXform(ast)
    
    print "Input Program"
    xform.codegen()
   
    xform.code_motion()
    
    print "Output Program"
    xform.codegen()

if __name__ == "__main__":
    cm_test()


        
