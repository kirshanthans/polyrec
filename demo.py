#!/usr/bin/python
import sys, os
from transformations import Transformation
from witnesstuples import WitnessTuple
from dependencetest import Dependence
from completion import Completion
from astxforms import ASTXform
from ast import *

def default():
    p = nest()
    # info about the program
    dim      = p.getdim()
    dim_type = p.getdimtype()
    in_alp   = p.getalp()
    in_ord   = p.getord()

    print "#Dims: ", dim
    print "Dimension Types:", dim_type
    print "Input Alphabet:", in_alp
    print "Input Order:", in_ord
    print "Source Code"
    print p.codegen()

def trans():
    pass

def deptest():
    pass

def complete():
    pass

def code():
    pass

def demo(option):
    if option == "transform":
        trans()
    elif option == "deptest":
        deptest()
    elif option == "complete":
        complete()
    elif option == "codegen":
        code()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        option = sys.argv[1]
        demo(option)
    else:
        default()
