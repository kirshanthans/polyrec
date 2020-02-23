import sys, os, copy, ast, astunparse
from pycparser import c_parser
from polyrec.pyast import Analyze
from polyrec.transformations import Transformation
from polyrec.pyastxforms import Transform
from polyrec.ctopy import CtoPy

def cm_test(filename):
    print("Code Motion Test")
    with open(filename, "r") as source:
        # reading the c file
        parser = c_parser.CParser()
        astc = parser.parse(source.read())
        # convert to python
        pysrc = CtoPy(astc)
        tree = ast.parse(pysrc.getPy())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # Output order
        out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]
        # Transform
        xf = Transformation(
            name         ='cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def ic_test(filename):
    print("Interchange Test")
    with open(filename, "r") as source:
        # reading the c file
        parser = c_parser.CParser()
        astc = parser.parse(source.read())
        # convert to python
        pysrc = CtoPy(astc)
        tree = ast.parse(pysrc.getPy())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # Transform
        xf = Transformation(
            name         ='ic',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            dim_i1       = 0,
            dim_i2       = 1)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def cm_ic_test(filename):
    with open(filename, "r") as source:
        # reading the c file
        parser = c_parser.CParser()
        astc = parser.parse(source.read())
        # convert to python
        pysrc = CtoPy(astc)
        tree = ast.parse(pysrc.getPy())
        analyze = Analyze(tree)
        xform = Transform(analyze)
        # Input program
        print("\nInput Program")
        print(xform.codegen())
        # Dimensions
        in_dim  = xform.analyze.dims
        out_dim = in_dim
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord() 
        # Output order
        out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]
        xf1 = Transformation(
            name         ='cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)
        xform.transform(xf1)
        # interchange
        dim1 = 0
        dim2 = 1
        xf2 = Transformation(
            name         ='ic',
            in_dim       = xf1.out_dim,
            out_dim      = xf1.out_dim,
            in_dim_type  = xf1.out_dim_type,
            in_alp       = xf1.out_alp,
            in_ord       = xf1.out_ord,
            dim_i1       = dim1,
            dim_i2       = dim2)
        xform.transform(xf2)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

if __name__ == "__main__":
    cm_ic_test("examples/sources/loop-rec.c")