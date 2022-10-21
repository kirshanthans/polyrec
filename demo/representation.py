from pycparser import c_parser, c_ast
import ast, astunparse
from polyrec.ctopy import CtoPy
from polyrec.pyast import Analyze
from polyrec.transformations import Transformation
from polyrec.pyastxforms import Transform
from polyrec.witnesstuples import WitnessTuple
from polyrec.dependencetest import Dependence

def representation(file):
    with open(file) as source:
        # reading the c file
        parser = c_parser.CParser()
        astc = parser.parse(source.read())
        # convert to python
        pysrc = CtoPy(astc)
        tree = ast.parse(pysrc.getPy())
        analyze = Analyze(tree)
        analyze.collect()
        xform = Transform(analyze)
        xform.analyze.depanalyze()
        # print info
        print("number of dimensions: ", analyze.getdim())
        print("every dimension type: ", analyze.getdimtype())
        print("alphabet for each dimension: ", analyze.getalp())
        print("order of statements: ", analyze.getord())
        print("index variables: ", analyze.getindvar())
        print("source code: ", analyze.codegen())
        print("Witness Tuples: ", xform.analyze.getdeps())

if __name__ == "__main__":
    representation("examples/sources/loop-rec.c")