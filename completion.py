#!/usr/bin/python
from transformations import Transformation
from dependencetest import Dependence
from witnesstuples import WitnessTuple

class Completion:
    def __init__(self, dims, dim_type, alphabet, order, partial, witness):
        assert dims == len(dim_type)
        assert dims == len(alphabet)
        assert dims == len(order)
        assert dims == len(partial)

        self.alphabet = alphabet # alphabet of input program
        self.order    = order    # input program order
        self.partial  = partial  # partial order of the output program
        self.witness  = witness  # list of witness tuples of the input program

        self.sanity = False # check partial order for sanity
        self.use_il = False # check the potential use of inlining
        self.use_sm = False # check the potential use of strip-mining

        self.completion_xform = []    # transformations for completion
        self.completion_exits = False # existence of completion
        self.completion_valid = False # validity of completion

    def check_sanity(self):
        pass

    def check_use_il(self):
        pass

    def check_use_sm(self):
        pass

    def completion_search(self):
        pass

    def completion_valid(self):
        pass

def completion_test():
    pass

if __name__ == "__main__":
    completion_test()