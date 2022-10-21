import sys, os, copy, ast, astunparse
from pycparser import c_parser
from polyrec.pyast import Analyze
from polyrec.transformations import Transformation
from polyrec.pyastxforms import Transform
from polyrec.ctopy import CtoPy
from polyrec.witnesstuples import WitnessTuple
from polyrec.dependencetest import Dependence
from polyrec.completion import Completion

def completion_test(filename):
    print("Completion Test")
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
        dim = xform.analyze.dims
        # Type of dimensions
        in_dim_type = xform.analyze.getdimtype()
        # Input alphabet and order
        in_alp = xform.analyze.getalp()
        in_ord = xform.analyze.getord()
        # partial order
        partial1 = [['t', 'r'], ['s', 'r', 'r']] # potential cm
        partial2 = [['r', 't'], ['s', 'r', 'r']] # potential cm-cm
        partial3 = [['t', 'r', 'r'], ['s', 'r']] # potential cm-ic

        xform.analyze.depanalyze()
        print(xform.analyze.getdeps())
        
        print("\nCompletion 1")
        comp1 = Completion(dim, in_dim_type, in_alp, in_ord, partial1, [Dependence(wt) for wt in xform.analyze.deps])
        comp1.checks()
        comp1.print_report()
        comp1.completion_search()
        comp1.print_pxforms()
        comp1.completion_valid()
        comp1.print_vxforms()

        print("\nCompletion 2")
        comp2 = Completion(dim, in_dim_type, in_alp, in_ord, partial2, [Dependence(wt) for wt in xform.analyze.deps])
        comp2.checks()
        comp2.print_report()
        comp2.completion_search()
        comp2.print_pxforms()
        comp2.completion_valid()
        comp2.print_vxforms()

        print("\nCompletion 3")
        comp3 = Completion(dim, in_dim_type, in_alp, in_ord, partial3, [Dependence(wt) for wt in xform.analyze.deps])
        comp3.checks()
        comp3.print_report()
        comp3.completion_search()
        comp3.print_pxforms()
        comp3.completion_valid()
        comp3.print_vxforms()

if __name__ == "__main__":
    completion_test("examples/sources/loop-rec.c")