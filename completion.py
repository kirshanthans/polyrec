#!/usr/bin/python
import itertools
from transformations import Transformation
from dependencetest import Dependence
from witnesstuples import WitnessTuple

class Completion:
    def __init__(self, in_dims, in_dim_type, in_alphabet, in_order, partial, deps):
        assert in_dims == len(in_dim_type)
        assert in_dims == len(in_alphabet)
        assert in_dims == len(in_order)
        assert in_dims <= len(partial)

        self.in_dims     = in_dims     # input program dimensions
        self.in_dim_type = in_dim_type # input program dimension types 
        self.in_alp      = in_alphabet # alphabet of input program
        self.in_ord      = in_order    # input program order
        self.partial     = partial     # partial order of the output program
        self.deps        = deps        # list of dependence objects of the input program

        self.sanity = False # check partial order for sanity
        self.use_ic = False # check the potential use of interchange
        self.use_il = False # check the potential use of inlining
        self.use_sm = False # check the potential use of strip-mining (Future use)

        self.pxforms = []    # potential transformations for completion (list of lists)
        self.vxforms = []    # valid transformations for completion (list of lists)

    def check_sanity(self): # simple sanity check for partial order
        for d in self.partial:
            if not 'r' in d:
                self.sanity = False
                return

        if not 's' in self.partial[-1]:
            self.sanity = False
            return

        for d in self.partial[:-1]:
            if not 't' in d:
                self.sanity = False
                return
        
        self.sanity = True
        return

    def check_use_ic(self): # check if the recursive labels are intact
        if self.use_sm: # it is not sensible to use sm alone
            self.use_ic = True
            return
        
        pg_ord = [d[1:] for d in self.in_ord] # ripping 'e' label
        pg_ord_typ = [list(map(lambda x: x[0], d)) for d in pg_ord] # getting the label types (~ partial)

        for i in xrange(self.in_dims-1):
            if self.partial[i].count('r') != pg_ord_typ[i].count('r'): # this is a weak check
                self.use_ic = True
    
    def check_use_il(self): # completion care for inlining only at the last level
        if self.partial[-1].count('s') == 1:
            return
        self.use_il = True

    def check_use_sm(self): # use of strip mining should be researched more - no test for now
        if self.in_dims == len(self.partial):
            return
        self.use_sm = True
    
    def checks(self): # all checks
        self.check_sanity()
        self.check_use_sm()
        self.check_use_ic()
        self.check_use_il()

    def print_report(self): # print summary of sanity checks
        print "\nInitial Report"
        if self.sanity:
            print "Partial order is sane"
        else:
            print "Partial order has errors"
            return
        
        if self.use_ic:
            print "Completion could use interchange"

        if self.use_il:
            print "Completion could use inlining"

        if self.use_sm:
            print "Completion could use strip-mining"

    def check_match(self, out_order): # check if an output order matches the given partial
        order = [d[1:] for d in out_order] # ripping the 'e' from each dimension

        if len(self.partial) != len(order): # checking for dimensions size match
            return False
        
        for i in xrange(len(self.partial)):
            if len(self.partial[i]) != len(order[i]): # checking for each dimension size match
                return False

        for i in xrange(len(self.partial)):
            for j in xrange(len(self.partial[i])):
                if self.partial[i][j] != order[i][j][0]: # checking for matching type of label in each dimension
                    return False                         # for example r matches 'r1', 'r2l' an 'r2r'
        
        return True
    
    def all_perm(self, d): # all permutations of a dimension
        assert d < self.in_dims

        order = list(self.in_ord[d][1:]) # dimension to find all permutations
        out_ords = [] # output order of all permutations

        for d_ord in itertools.permutations(order): # finding all permutation
            out_ords.append(['e'] + list(d_ord))

        return out_ords

    def cm_out_ords(self): # all combinations of codemotion output orders
        alldim = [] 
        for d in xrange(self.in_dims): # finding all permutations of all dimensions
            alldim.append(self.all_perm(d))
        
        out_ords = []
        for out_ord in itertools.product(*alldim): # taking the cross product of these different orders
            if list(out_ord) == self.in_ord:
                continue
            out_ords.append(list(out_ord))

        return out_ords

    @staticmethod
    def next_pcm(xf): # takes transformation and returns a list of next possible xforms that are code motion
        nxt_xfs = []
        out_ords = Completion.ord_permutation(xf.out_ord, xf.out_dim)
        for out_ord in out_ords:
            xf = Transformation(
                name         = 'cm',
                in_dim       = xf.out_dim,
                out_dim      = xf.out_dim,
                in_dim_type  = xf.out_dim_type,
                in_alp       = xf.out_alp,
                in_ord       = xf.out_ord,
                out_ord      = out_ord)
            nxt_xfs.append(xf)

        return nxt_xfs
    
    @staticmethod
    def next_pic(xf): # takes transformation and returns a list of next possible xforms that are interchange
        nxt_xfs = []
        for d in xrange(xf.out_dims-1):
            xf = Transformation(
                name         ='ic',
                in_dim       = xf.out_dim,
                out_dim      = xf.out_dim,
                in_dim_type  = xf.out_dim_type,
                in_alp       = xf.out_alp,
                in_ord       = xf.out_ord,
                dim_i1       = d,
                dim_i2       = d+1)
            nxt_xfs.append(xf)
        
        return nxt_xfs
            

    def completion_search(self):
        init_xfs = [] # seed xforms to further the chain

        cm_xfs = [] # contians any cm xform that does not match the partial order to further the chain
        out_ords = Completion.ord_permutation(self.in_ord, self.in_dims) # all possible different combinations of cm xforms
        for out_ord in out_ords:
            xf = Transformation(
                name         = 'cm',
                in_dim       = self.in_dims,
                out_dim      = self.in_dims,
                in_dim_type  = self.in_dim_type,
                in_alp       = self.in_alp,
                in_ord       = self.in_ord,
                out_ord      = out_ord)
            
            if self.check_match(xf.out_ord):
                self.pxforms.append([xf])
            else:
                cm_xfs.append(xf)
        
        if self.use_ic:
            ic_xfs = [] # contains any ic xform that does not match the partial order to further the chain
            for d in xrange(self.in_dims-1):
                xf = Transformation(
                    name         ='ic',
                    in_dim       = self.in_dims,
                    out_dim      = self.in_dims,
                    in_dim_type  = self.in_dim_type,
                    in_alp       = self.in_alp,
                    in_ord       = self.in_ord,
                    dim_i1       = d,
                    dim_i2       = d+1)

                if self.check_match(xf.out_ord):
                    self.pxforms.append([xf])
                else:
                    ic_xfs.append(xf)
    
    def print_pxforms(self):
        print "\nPotential Transformations"
        for xfs,i in zip(self.pxforms, xrange(len(self.pxforms))):
            print "xform ", i
            print "\t", xfs[0].to_string()
            for xf in xfs[1:]:
                print "\t", xf.to_string()
    
    def completion_valid(self):
        if len(self.pxforms) == 0:
            return
        
        for xfs in self.pxforms:
            xform = xfs[0]
            for x in xfs[1:]:
                xform = xform.compose(x)
            
            for d in self.deps:
                if ~d.test(xform):
                    break
            
            self.vxforms.append(xfs)

    def print_vxforms(self):
        print "\nValid Transformations"
        for xfs,i in zip(self.vxforms, xrange(len(self.vxforms))):
            print "xform ", i
            print "\t", xfs[0].to_string()
            for xf in xfs[1:]:
                print "\t", xf.to_string()

def completion_test():
    print "Completion Test"
    # dims
    dim = 2
    # dim type
    dim_type = [1, 2]
    # Input alphabet and order
    alp1 = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1 = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # partial order
    partial1 = [['t', 'r'], ['s', 'r', 'r']] # potential cm
    partial2 = [['r', 't'], ['s', 'r', 'r']] # potential cm-cm
    partial3 = [['t', 'r', 'r'], ['s', 'r']] # potential cm-ic
    # witness tuple
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    wtuple1 = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple1.set_fsa()

    print "\nCompletion 1"
    comp1 = Completion(dim, dim_type, alp1, ord1, partial1, [Dependence(wtuple1)])
    comp1.checks()
    comp1.print_report()
    comp1.completion_search()
    comp1.print_pxforms()
    comp1.completion_valid()
    comp1.print_vxforms()

    # comp2 = Completion(dim, dim_type, alp1, ord1, partial2, [Dependence(wtuple1)])
    # comp2.checks()
    # print "Completion 2"
    # comp2.print_report()

    # comp3 = Completion(dim, dim_type, alp1, ord1, partial3, [Dependence(wtuple1)])
    # comp3.checks()
    # print "Completion 3"
    # comp3.print_report()

if __name__ == "__main__":
    completion_test()