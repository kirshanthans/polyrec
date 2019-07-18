#!/usr/bin/python3
import sys, os
from polyrec.transformations import Transformation
from polyrec.witnesstuples import WitnessTuple
from polyrec.dependencetest import Dependence
from polyrec.completion import Completion
from polyrec.astxforms import ASTXform
from polyrec.ast import *

def default():
    p = nest()
    # info about the program
    dim      = p.getdim()
    dim_type = p.getdimtype()
    in_alp   = p.getalp()
    in_ord   = p.getord()

    print("#Dims: ", dim)
    print("Dimension Types:", dim_type)
    print("Input Alphabet:", in_alp)
    print("Input Order:", in_ord)
    print("Source Code")
    print(p.codegen())

def trans():
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

    # Strip Mining
    strip_dim  = 0
    strip_size = 2

    xform2 = Transformation(
        name        = 'sm',
        in_dim      = xform1.out_dim,
        out_dim     = xform1.out_dim+1,
        in_dim_type = xform1.out_dim_type,
        in_alp      = xform1.out_alp,
        in_ord      = xform1.out_ord,
        dim_strip   = strip_dim,
        strip_size  = strip_size)

    # Interchange
    dim1_ = 1
    dim2_ = 2
    
    xform3 = Transformation(
        name         ='ic',
        in_dim       = xform2.out_dim,
        out_dim      = xform2.out_dim,
        in_dim_type  = xform2.out_dim_type,
        in_alp       = xform2.out_alp,
        in_ord       = xform2.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)

    # Inline
    dim_il   = 1
    call_il  = 1
    label_il = 'l'
    
    xform4 = Transformation(
        name        = 'il',
        in_dim      = xform3.out_dim,
        out_dim     = xform3.out_dim,
        in_dim_type = xform3.out_dim_type,
        in_alp      = xform3.out_alp,
        in_ord      = xform3.out_ord,
        dim_inline  = dim_il,
        call_inline = call_il,
        label       = label_il)

    xform = xform1.compose(xform2).compose(xform3).compose(xform4)

    xform.input_program()
    print("\nTransformation: ", xform.name)
    xform.output_program()

def deptest():
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

    # Strip Mining
    strip_dim  = 0
    strip_size = 2

    xform2 = Transformation(
        name        = 'sm',
        in_dim      = xform1.out_dim,
        out_dim     = xform1.out_dim+1,
        in_dim_type = xform1.out_dim_type,
        in_alp      = xform1.out_alp,
        in_ord      = xform1.out_ord,
        dim_strip   = strip_dim,
        strip_size  = strip_size)

    # Interchange
    dim1_ = 1
    dim2_ = 2
    
    xform3 = Transformation(
        name         ='ic',
        in_dim       = xform2.out_dim,
        out_dim      = xform2.out_dim,
        in_dim_type  = xform2.out_dim_type,
        in_alp       = xform2.out_alp,
        in_ord       = xform2.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)

    # Inline
    dim_il   = 1
    call_il  = 1
    label_il = 'l'
    
    xform4 = Transformation(
        name        = 'il',
        in_dim      = xform3.out_dim,
        out_dim     = xform3.out_dim,
        in_dim_type = xform3.out_dim_type,
        in_alp      = xform3.out_alp,
        in_ord      = xform3.out_ord,
        dim_inline  = dim_il,
        call_inline = call_il,
        label       = label_il)

    xform = xform1.compose(xform2).compose(xform3).compose(xform4)
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]

    print("suffix1: ", rgx1)
    print("suffix2: ", rgx2)
    
    wtuple = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple.set_fsa()

    Dep = Dependence(wtuple)

    print("Input Program")
    xform.input_program()
    print("Output Program")
    xform.output_program()

    if Dep.test(xform):
        print("Dependence is preserved")
    else:
        print("Dependence is broken")

def complete():
    # dims
    dim = 2
    # dim type
    dim_type = [1, 2]
    # Input alphabet and order
    alp1 = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1 = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # partial order
    partial = [['t', 'r'], ['s', 's', 'r', 'r', 'r']] # potential cm-il
    print("Partial Order: ", partial)
    # witness tuple
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    print("suffix1: ", rgx1)
    print("suffix2: ", rgx2)
    wtuple = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple.set_fsa()
    # completion   
    print("Completion")
    comp = Completion(dim, dim_type, alp1, ord1, partial, [Dependence(wtuple)])
    comp.checks()
    comp.print_report()
    comp.completion_search()
    comp.print_pxforms()
    comp.completion_valid()
    comp.print_vxforms()

def code():
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
    
    print("Output Program cm-ic-il")
    print(xform.codegen())

def demo(option):
    if option == "transform":
        trans()
    elif option == "deptest":
        deptest()
    elif option == "complete":
        complete()
    elif option == "codegen":
        code()
    else:
        default()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        option = sys.argv[1]
        demo(option)
    else:
        default()
