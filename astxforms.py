#!/usr/bin/python
import sys, os
from transformations import Transformation
from ast import *

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


        
