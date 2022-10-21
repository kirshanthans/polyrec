import sys, os, copy, ast, astunparse
from pycparser import c_parser
from polyrec.pyast import Analyze
from polyrec.transformations import Transformation
from polyrec.pyastxforms import Transform
from polyrec.ctopy import CtoPy
from polyrec.witnesstuples import WitnessTuple
from polyrec.dependencetest import Dependence

def deptest_cm(filename):   
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

        xf = Transformation(
            name         ='cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)

        xform.analyze.depanalyze()
        print(xform.analyze.getdeps())
        for i, wt in enumerate(xform.analyze.deps):
            Dep = Dependence(wt)
            print("Witness Tuple", i, ": ", Dep.test(xf))
    
def deptest_ic(filename):
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

        xf = Transformation(
            name         ='ic',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            dim_i1       = 0,
            dim_i2       = 1)
    
        xform.analyze.depanalyze()
        print(xform.analyze.getdeps())
        for i, wt in enumerate(xform.analyze.deps):
            Dep = Dependence(wt)
            print("Witness Tuple", i, ": ", Dep.test(xf))

def deptest_cm_ic(filename):
    print("CM-IC Test")
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
            name         = 'cm',
            in_dim       = in_dim,
            out_dim      = out_dim,
            in_dim_type  = in_dim_type,
            in_alp       = in_alp,
            in_ord       = in_ord,
            out_ord      = out_ord)

        # interchange
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

        xf = xf1.compose(xf2)

        xform.analyze.depanalyze()
        print(xform.analyze.getdeps())
        for i, wt in enumerate(xform.analyze.deps):
            Dep = Dependence(wt)
            print("Witness Tuple", i, ": ", Dep.test(xf))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("provide proper argument")
        exit()
    test = sys.argv[1]
    if test == "cm":
        deptest_cm("examples/sources/loop-rec.c")
    elif test == "ic":
        deptest_ic("examples/sources/loop-rec.c")
    elif test == "cm-ic":
        deptest_cm_ic("examples/sources/loop-rec.c")