#!/usr/bin/python
import sys, os
from ast import *

class ASTXform:
    def __init__(self, ast):
        self.ast = ast

    def code_motion(self):
        pass

    def inter_change(self):
        pass

    def inlining(self):
        pass

    def strip_mining(self):
        pass

    def codegen(self):
        
        return self.ast.codegen()

def test_cm():
    ast = None 
    
    xform = ASTXform(ast)
    
    print "Input Program"
    xform.codegen()
   
    xform.code_motion()
    
    print "Output Program"
    xform.codegen()

if __name__ == "__main__":
    test_cm()


        
