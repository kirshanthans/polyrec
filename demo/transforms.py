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

def sm_test(filename):
    print("Strip Mining Test")
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
        out_dim = in_dim + 1
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # strip dimension
        strip_dim = 0
        # strip size
        strip_size = 2
        # Transform
        xf = Transformation(
            name        = 'sm',
            in_dim      = in_dim, 
            out_dim     = out_dim, 
            in_dim_type = in_dim_type, 
            in_alp      = in_alp, 
            in_ord      = in_ord, 
            dim_strip   = strip_dim, 
            strip_size  = strip_size)
        xform.transform(xf)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

def cm_sm_ic_test(filename):
    print("CM-SM-IC Test")
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
        
        # code-motion
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
        
        # strip mining
        # strip dimension
        strip_dim = 0
        # strip size
        strip_size = 2
        # Transform
        xf2 = Transformation(
            name        = 'sm',
            in_dim      = xf1.out_dim, 
            out_dim     = xf1.out_dim+1, 
            in_dim_type = xf1.in_dim_type, 
            in_alp      = xf1.out_alp, 
            in_ord      = xf1.out_ord, 
            dim_strip   = strip_dim, 
            strip_size  = strip_size)
        xform.transform(xf2)
        
        # interchange
        # dimensions
        dim1 = 1
        dim2 = 2
        xf3 = Transformation(
            name         ='ic',
            in_dim       = xf2.out_dim,
            out_dim      = xf2.out_dim,
            in_dim_type  = xf2.out_dim_type,
            in_alp       = xf2.out_alp,
            in_ord       = xf2.out_ord,
            dim_i1       = dim1,
            dim_i2       = dim2)
        xform.transform(xf3)
        # Output program
        print("\nOutput Program")
        print(xform.codegen())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("provide proper argument")
        exit()
    test = sys.argv[1]
    if test == "cm":
        cm_test("examples/sources/loop-rec.c")
    elif test == "sm":
        sm_test("examples/sources/loop-rec.c")
    elif test == "ic":
        ic_test("examples/sources/loop-rec.c")
    elif test == "cm-sm-ic":
        cm_sm_ic_test("examples/sources/loop-rec.c")