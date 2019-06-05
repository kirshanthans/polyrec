#!/usr/bin/python
import sys, os
from statemachines import MultiTapeFSA

class WitnessTuple:
    def __init__(self, dims, dim_type, alphabet, order, regex1, regex2):
        assert dims == len(dim_type)
        assert dims == len(alphabet)
        assert dims == len(order)
        assert dims == len(regex1)
        assert dims == len(regex2)

        self.dims     = dims
        self.dim_type = dim_type
        self.alp      = alphabet
        self.ord      = order
        self.regex1   = regex1
        self.regex2   = regex2
        self.fsa1     = None
        self.fsa2     = None

    def get_num_states(self, num):
        n = self.dims + 1
        regx = []
        if num == 1:
            regx = self.regex1
        else:
            regx = self.regex2
            
        for i in xrange(self.dims):
            for exp in regx[i][:-1]:
                if exp[-1] != '*':
                    n += 1
        
        return n

    def get_init_states(self, num):
        return [0]

    def get_final_states(self, num, num_states):
        return [num_states-1]

    def complete_fsa(self, num):
        regx = []
        fsa  = None
        n    = 0
        if num == 1:
            regx = self.regex1
            fsa  = self.fsa1
            n    = self.fsa1.nstates
        else:
            regx = self.regex2
            fsa  = self.fsa2
            n    = self.fsa2.nstates
        
        s_trans = n - (self.dims + 1)
        for i in xrange(self.dims):
            tup = ['e'] * self.dims
            tup[i] = regx[i][-1]
            fsa.add_transition(s_trans, s_trans+1, tuple(tup))
            s_trans += 1
        
        s_recur = 0
        for i in xrange(self.dims):
            for exp in regx[i][:-1]:
                if exp[-1] != '*':
                    if '|' in exp:
                        labels = exp.split('|')
                        labels = [l.replace('(', '') for l in labels]
                        labels = [l.replace(')', '') for l in labels]

                        for l in labels:
                            assert l in self.alp[i]
                            tup = ['e'] * self.dims
                            tup[i] = l
                            fsa.add_transition(s_recur, s_recur+1, tuple(tup))
                    else:
                        label = exp.replace('(', '').replace(')', '')

                        assert label in self.alp[i]
                        tup = ['e'] * self.dims
                        tup[i] = label
                        fsa.add_transition(s_recur, s_recur+1, tuple(tup))

                    s_recur += 1
                else:
                    if '|' in exp:
                        labels = exp[:-1].split('|')
                        labels = [l.replace('(', '') for l in labels]
                        labels = [l.replace(')', '') for l in labels]
                        
                        for l in labels:
                            assert l in self.alp[i]
                            tup = ['e'] * self.dims
                            tup[i] = l
                            fsa.add_transition(s_recur, s_recur, tuple(tup))
                    else:
                        label = exp[:-1].replace('(', '').replace(')', '')
                        
                        assert label in self.alp[i]
                        tup = ['e'] * self.dims
                        tup[i] = label
                        fsa.add_transition(s_recur, s_recur, tuple(tup))

    def set_fsa(self):

        n1 = self.get_num_states(1)
        n2 = self.get_num_states(2)

        init1 = self.get_init_states(1)
        init2 = self.get_init_states(2)

        final1 = self.get_final_states(1, n1)
        final2 = self.get_final_states(2, n2)

        self.fsa1 = MultiTapeFSA(n1, init1, final1, self.dims, self.alp, self.ord)
        self.fsa2 = MultiTapeFSA(n2, init2, final2, self.dims, self.alp, self.ord)

        self.complete_fsa(1)
        self.complete_fsa(2)

def witness_test():
    # dims
    dim = 2
    # dim type
    dim_type = [1, 2]
    # Input alphabet and order
    alp1 = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1 = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    rgx3 = [['r1', 't1'], ['s1']]
    rgx4 = [['t1'], ['(r2l|r2r)','s1']]
    rgx5 = [['r1','t1'], ['(r2l|r2r)','s1']]

    print "Witness Tuple 1"
    wtuple1 = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple1.set_fsa()
    print "Suffix 1"
    wtuple1.fsa1.print_fsa()
    print "Suffix 2"
    wtuple1.fsa2.print_fsa()
    
    print "Witness Tuple 2"
    wtuple2 = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx4)
    wtuple2.set_fsa()
    print "Suffix 1"
    wtuple2.fsa1.print_fsa()
    print "Suffix 2"
    wtuple2.fsa2.print_fsa()
    
    print "Witness Tuple 3"
    wtuple3 = WitnessTuple(dim, dim_type, alp1, ord1, rgx3, rgx5)
    wtuple3.set_fsa()
    print "Suffix 1"
    wtuple3.fsa1.print_fsa()
    print "Suffix 2"
    wtuple3.fsa2.print_fsa()

if __name__ == "__main__":
    witness_test()
