#!/usr/bin/python
from transformations import Transformation
from witnesstuples import WitnessTuple
from dependencetest import Dependence
from completion import Completion
from astxforms import ASTXform
from ast import *

def demo():
    p = nest()
    # info about the program
    dim      = p.getdim()
    dim_type = p.getdimtype()
    in_alp   = p.getalp()
    in_ord   = p.getord()

if __name__ == "__main__":
    demo()

