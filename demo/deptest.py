import sys, os, copy, ast, astunparse
from pycparser import c_parser
from polyrec.pyast import Analyze
from polyrec.transformations import Transformation
from polyrec.pyastxforms import Transform
from polyrec.ctopy import CtoPy
from polyrec.witnesstuples import WitnessTuple
from polyrec.dependencetest import Dependence

def deptest_cm():   
    print("Code Motion Test")
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

    xform = Transformation(
        name         ='cm',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        out_ord      = out_ord)

    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))
 
def deptest_ic():
    print("Interchange Test")
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    xform = Transformation(
        name         ='ic',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        dim_i1       = 0,
        dim_i2       = 1)
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))

def deptest_cm_ic():
    print("CM-IC Test")
    # Dimensions
    dim  = 2
    # Type of dimensions
    dim_type = [1, 2]

    # code-motion 
    alp1  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    ord2  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    xform1 = Transformation(
        name         = 'cm',
        in_dim       = dim,
        out_dim      = dim,
        in_dim_type  = dim_type,
        in_alp       = alp1,
        in_ord       = ord1,
        out_ord      = ord2)
    
    # interchange
    dim1_ = 0
    dim2_ = 1
    
    xform2 = Transformation(
        name         ='ic',
        in_dim       = xform1.out_dim,
        out_dim      = xform1.out_dim,
        in_dim_type  = xform1.out_dim_type,
        in_alp       = xform1.out_alp,
        in_ord       = xform1.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)
    
    xform = xform1.compose(xform2)
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(dim, dim_type, alp1, ord1, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))

if __name__ == "__main__":
    deptest_cm()