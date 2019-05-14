#!/usr/bin/python
import sys, os

class MultiTapeFSA():
    def __init__(self, nstates, initstates, finalstates, dim, alphabet, order):
        
        for s in initstates:
            assert s < nstates 
        for s in finalstates:
            assert s < nstates

        assert len(alphabet) == dim
        assert len(order) == dim

        for a in alphabet:
            assert len(a) == len(set(a))
        for o in order:
            assert len(o) == len(set(o))
        
        self.nstates      = nstates
        self.states       = tuple(range(nstates))
        self.init_states  = tuple(initstates)
        self.final_states = tuple(finalstates)
        self.dims         = dim
        self.alphabet     = tuple(alphabet)
        self.order        = tuple(order)
        self.transitions  = set()
        self.edges        = {}
        self.edges_in     = {}
   
    def print_fsa(self):
        
            print "nstates ", self.nstates
            print ""
      
            print "Init States" 
            for e in self.init_states:
                print e,
            print ""
       
            print "Final States "
            for e in self.final_states:
                print e,
            print ""
        
            print "Alphabet "
            for tape, dim in zip(self.alphabet, range(self.dims)):
                print "Dim ", dim, ": ",
                for e in tape:
                    print e,
                print ""
            print ""

            print "Order "
            for tape, dim in zip(self.order, range(self.dims)):
                print "Dim ", dim, ": ",
                for e in tape:
                    print e,
                print ""
            print ""
            
            print "Transitions "
            for e in sorted(self.transitions):
                print e
            print ""

            print "Edges "
            for e in self.edges:
                print e, self.edges[e]

    def add_transition(self, start, end, tup):

        assert len(tup) == self.dims

        for dim in range(self.dims):
            assert tup[dim] in self.alphabet[dim]

        self.transitions.add((start, end, tup))

        if start in self.edges:
            self.edges[start].append((end, tup))
        else:
            self.edges[start] = [(end, tup)] 
        
        if end in self.edges_in:
            self.edges_in[end].append((start, tup))
        else:
            self.edges_in[end] = [(start, tup)]

    def identity_fst(self):

        fst_id = MultiTapeFST(self.nstates, self.init_states, self.final_states, self.dims, self.dims, self.alphabet, self.alphabet, self.order, self.order)

        for (start, end, tuple_in) in self.transitions:
            fst_id.add_transition(start, end, tuple_in, tuple_in)
        
        return fst_id

    def unreachable_removal(self):
        unreachable_states = set(self.states)
        unreachable_states -= set(self.edges_in.keys())
        unreacheable_states = unreachable_states.union(set(self.edges.keys())-set(self.edges_in.keys()).intersection(set(self.edges.keys())))
        unreachable_states -= set(self.init_states)
        
        new_states = list(set(self.states) - unreachable_states)
        new_states.sort()
        new_nstates = len(new_states)
        new_initstates = list(self.init_states)
        new_ninitstates = len(new_initstates)
        new_finalstates = list(set(self.final_states) - unreachable_states)
        new_nfinalstates = len(new_finalstates)

        new_fsa = MultiTapeFSA(new_nstates, range(new_ninitstates), range(new_nstates-new_nfinalstates, new_nstates) , self.dims, self.alphabet, self.order)
        map_nstates = {}
        for i, e in zip(range(new_nstates), new_states):
            map_nstates[e] = i
        
        for start, end, tup in self.transitions:
            if start not in unreachable_states:
                new_fsa.add_transition(map_nstates[start], map_nstates[end], tup)
            
        return new_fsa

class MultiTapeFST():
    def __init__(self, nstates, initstates, finalstates, dimin, dimout, alphabetins, alphabetouts, orderins, orderouts):
        
        for s in initstates:
            assert s < nstates 
        for s in finalstates:
            assert s < nstates

        assert len(alphabetins) == dimin
        assert len(alphabetouts) == dimout
        assert len(orderins) == dimin
        assert len(orderouts) == dimout

        for alphabet in alphabetins:
            assert len(alphabet) == len(set(alphabet))
        for alphabet in alphabetouts:
            assert len(alphabet) == len(set(alphabet))
        for order in orderins:
            assert len(order) == len(set(order))
        for order in orderouts:
            assert len(order) == len(set(order))
        
        self.nstates      = nstates
        self.states       = tuple(range(nstates))
        self.init_states  = tuple(initstates)
        self.final_states = tuple(finalstates)
        self.dims_in      = dimin
        self.dims_out     = dimout
        self.alphabet_in  = tuple(alphabetins)
        self.alphabet_out = tuple(alphabetouts)
        self.ord_in       = tuple(orderins)
        self.ord_out      = tuple(orderouts)
        self.transitions  = set()
        self.edges        = {}

    def add_transition(self, start, end, tuplein, tupleout):

        assert len(tuplein) == self.dims_in
        assert len(tupleout) == self.dims_out

        for dim in range(self.dims_in):
            assert tuplein[dim] in self.alphabet_in[dim]
        for dim in range(self.dims_out):
            assert tupleout[dim] in self.alphabet_out[dim]

        self.transitions.add((start, end, tuplein, tupleout))

        if start in self.edges:
            self.edges[start].append((end, tuplein, tupleout))
        else:
            self.edges[start] = [(end, tuplein, tupleout)]

    def print_fst(self):
        
        print "nstates ", self.nstates
        print ""
      
        print "Init States" 
        for e in self.init_states:
            print e,
        print ""
       
        print "Final States "
        for e in self.final_states:
            print e,
        print ""
        
        print "Input Alphabet "
        for tape, dim in zip(self.alphabet_in, range(self.dims_in)):
            print "Dim ", dim, ": ",
            for e in tape:
                print e,
            print ""
        print ""
            
        print "Input Order "
        for tape, dim in zip(self.ord_in, range(self.dims_in)):
            print "Dim ", dim, ": ",
            for e in tape:
                print e,
            print ""
        print ""
        
        print "Output Alphabet "
        for tape, dim in zip(self.alphabet_out, range(self.dims_out)):
            print "Dim ", dim, ": ",
            for e in tape:
                print e,
            print ""
        print ""
        
        print "Output Order "
        for tape, dim in zip(self.ord_out, range(self.dims_out)):
            print "Dim ", dim, ": ",
            for e in tape:
                print e,
            print ""
        print ""
        
        print "Transitions "
        for e in sorted(self.transitions):
            print e
        print ""

        print "Edges "
        for e in self.edges:
            print e, self.edges[e]
    
    def project_in(self):
        
        fsa_in = MultiTapeFSA(self.nstates, self.init_states, self.final_states, self.dims_in, self.alphabet_in, self.ord_in)
        for (start, end, tuple_in, _) in self.transitions:
            fsa_in.add_transition(start, end, tuple_in)

        return fsa_in

    def project_out(self):
        
        fsa_out = MultiTapeFSA(self.nstates, self.init_states, self.final_states, self.dims_out, self.alphabet_out, self.ord_out)
        for (start, end, _, tuple_out) in self.transitions:
            fsa_out.add_transition(start, end, tuple_out)

        return fsa_out

    def state_compose(self, state1, state2, nstates2):

        return state1 * nstates2 + state2
    
    def cross_product(self, state1, state2, nstates2):
        
        return [self.state_compose(i, j, nstates2) for i in state1 for j in state2]

    def compose_fst(self, fst):
        #always left to right (self * fst)
        assert self.alphabet_out == fst.alphabet_in

        nstates_     = self.nstates * fst.nstates
        initstates_  = self.cross_product(self.init_states, fst.init_states, fst.nstates)
        finalstates_ = self.cross_product(self.final_states, fst.final_states, fst.nstates)
        alphabetin_  = self.alphabet_in
        orderin_     = self.ord_in
        dimin_       = self.dims_in
        alphabetout_ = fst.alphabet_out
        orderout_    = fst.ord_out
        dimout_      = fst.dims_out

        fst_ = MultiTapeFST(nstates_, initstates_, finalstates_, dimin_, dimout_, alphabetin_, alphabetout_, orderin_, orderout_)

        for t1 in self.transitions:
            for t2 in fst.transitions:
                if t1[3] == t2[2] or t1[3] == tuple(['e'] * self.dims_out) or t2[2] == tuple(['e'] * fst.dims_in):
                    fst_.add_transition(self.state_compose(t1[0], t2[0], fst.nstates), 
                                        self.state_compose(t1[1], t2[1], fst.nstates), 
                                        t1[2], t2[3])

        return fst_

def construct_fst_lr2lr(fst):
    #in_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #out_alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #setting the alphabets
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    # setting the transistions
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[2]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[3]))

def simple_prog(fsa):
    alph_dim1 = fsa.alphabet[0]
    alph_dim2 = fsa.alphabet[1]

    fsa.add_transition(0, 0, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(0, 0, (alph_dim1[0], alph_dim2[1]))
    fsa.add_transition(0, 0, (alph_dim1[0], alph_dim2[2]))
    fsa.add_transition(0, 1, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[3]))

def construct_fst_llr2llr(fst):
    #in_alp  : [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    #out_alp : [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    in_alph_dim3  = fst.alphabet_in[2]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]
    out_alph_dim3 = fst.alphabet_out[2]

    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[1], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[1], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[1]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[2]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[2], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(2, 3, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[3]))

def construct_fst_rl2rl(fst):
    #in_alp : [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    #out_alp: [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    # setting the transistions
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(0, 1, (in_alph_dim1[3], in_alph_dim2[0]), (out_alph_dim1[3], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[2]))

def construct_fst_lrl2lrl(fst):
    #in_alp  : [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    #out_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 't2'], ['e', 'r3', 's1']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    in_alph_dim3  = fst.alphabet_in[2]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]
    out_alph_dim3 = fst.alphabet_out[2]

    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[1], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[1]), (out_alph_dim1[0], out_alph_dim2[1], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[2]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[2], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[3], out_alph_dim3[0]))
    fst.add_transition(2, 3, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))

def construct_fst_lr2rl(fst):
    #in_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #out_alp: [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    #setting the alphabets
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    # setting the transistions
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[3], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[2]))

def construct_fst_llr2lrl(fst):
    #in_alp  : [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    #out_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 't2'], ['e', 'r3', 's1']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    in_alph_dim3  = fst.alphabet_in[2]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]
    out_alph_dim3 = fst.alphabet_out[2]

    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[1], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[1]), (out_alph_dim1[0], out_alph_dim2[1], out_alph_dim3[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[2]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0], in_alph_dim3[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[2], in_alph_dim3[0]), (out_alph_dim1[0], out_alph_dim2[3], out_alph_dim3[0]))
    fst.add_transition(2, 3, (in_alph_dim1[0], in_alph_dim2[0], in_alph_dim3[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))

def construct_fst_rl2lr(fst):
    #in_alp : [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    #out_alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #setting the alphabets
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    # setting the transistions
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(0, 0, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[2]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 1, (in_alph_dim1[3], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[3]))

def construct_fst_lrl2llr(fst):
    pass

def construct_fst_il_llr(fst):
    #input_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #output_alp: [['e', 'r1', 't1'], ['e', 'rll2', 'rlr2', 'rr2', 's1', 's2']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    #add transition
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[3]))
    fst.add_transition(3, 3, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 3, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[0]))
    fst.add_transition(3, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(3, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[2]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[4]))
    fst.add_transition(3, 4, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(4, 5, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[5]))

def construct_fst_il_lrr(fst):
    #input_alp : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #output_alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rrl2', 'rrr2', 's1', 's2']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]

    #add transition
    fst.add_transition(0, 0, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[1]))
    fst.add_transition(3, 3, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0]))
    fst.add_transition(0, 3, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[0]))
    fst.add_transition(3, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[2]))
    fst.add_transition(3, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[3]))
    fst.add_transition(0, 1, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(1, 2, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[4]))
    fst.add_transition(3, 4, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0]))
    fst.add_transition(4, 5, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[5]))

def construct_fst_lr2llr(fst):
    #in_alp  : [['e', 'r1', 't1'], ['e', 'rl2', 'rr2' 's1']]
    #out_alp : [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    in_alph_dim1  = fst.alphabet_in[0]
    in_alph_dim2  = fst.alphabet_in[1]
    out_alph_dim1 = fst.alphabet_out[0]
    out_alph_dim2 = fst.alphabet_out[1]
    out_alph_dim3 = fst.alphabet_out[2]

    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(0, 0, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))
    fst.add_transition(0, 4, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[1], out_alph_dim3[0]))
    fst.add_transition(0, 1, (in_alph_dim1[0], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(1, 2, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(2, 3, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[3]))

    fst.add_transition(4, 4, (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(4, 4, (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))
    fst.add_transition(4, 8, (in_alph_dim1[1], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[1], out_alph_dim3[0]))
    fst.add_transition(4, 5, (in_alph_dim1[0], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(5, 6, (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(6, 7, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[3]))

    fst.add_transition(8, 8,   (in_alph_dim1[0], in_alph_dim2[1]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[1]))
    fst.add_transition(8, 8,   (in_alph_dim1[0], in_alph_dim2[2]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[2]))
    fst.add_transition(8, 0,   (in_alph_dim1[0], in_alph_dim2[0]), (out_alph_dim1[1], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(8, 9,   (in_alph_dim1[0], in_alph_dim2[0]), (out_alph_dim1[2], out_alph_dim2[0], out_alph_dim3[0]))
    fst.add_transition(9, 10,  (in_alph_dim1[2], in_alph_dim2[0]), (out_alph_dim1[0], out_alph_dim2[2], out_alph_dim3[0]))
    fst.add_transition(10, 11, (in_alph_dim1[0], in_alph_dim2[3]), (out_alph_dim1[0], out_alph_dim2[0], out_alph_dim3[3]))

def construct_sample_suffix_fsa0(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[t1, s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]

    fsa.add_transition(0, 1, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa1(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[r1+t1, s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa2(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[r1t1, s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa3(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[t1, rl2s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[0], alph_dim2[1]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa4(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[t1, rr2s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[0], alph_dim2[2]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa5(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[r1t1, rl2s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[1]))
    fsa.add_transition(2, 3, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(3, 4, (alph_dim1[0], alph_dim2[3]))

def construct_sample_suffix_fsa6(fsa):
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #[r1t1, rr2s1]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[2]))
    fsa.add_transition(2, 3, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(3, 4, (alph_dim1[0], alph_dim2[3]))

def construct_dict(list_of_alphabet):
    #construct an alphabetically ordered dictionary per dimension
    dims = len(list_of_alphabet)
    list_ret = []
    for i in xrange(dims):
        rank = {}
        alphabet = list_of_alphabet[i]
        for j in xrange(len(alphabet)):
            rank[alphabet[j]] = j-1
        list_ret.append(rank)
    return list_ret

def find_edge_latest(curr_state, fsa, dims, list_of_dict):
    #finding the latest edge from a given state
    next_state = None
    alph = 'e'
    dim = -1
    rank = -1
    
    outgoing = fsa.edges[curr_state]
    for i in xrange(dims):
        dict_dim = list_of_dict[i]
        for end, tup in outgoing:
            rank_ = dict_dim[tup[i]]
            alph_ = tup[i]
            if rank_ >= 0 and rank_ > rank:
                rank = rank_
                alph = alph_
                dim  = i
                next_state = end
        if alph is not 'e':
            break

    return alph, dim, next_state

def latest_path(fsa, list_of_dict):
    #designed to handle one initial state
    #list of dict gives the alphabetical order by dimension
    init_state = fsa.init_states[0]
    dims = fsa.dims
    assert len(list_of_dict) == dims

    path = {}
    for i in xrange(dims):
        path[i] = []
    state_chain = []

    curr_state = init_state

    while curr_state not in state_chain and curr_state not in fsa.final_states:
        
        if len(fsa.edges[curr_state]) == 1 and fsa.edges[curr_state][0][1] == tuple(['e']*dims):
            state_chain.append(curr_state)
            curr_state = fsa.edges[curr_state][0][0]
        
        alph, dim, next_state = find_edge_latest(curr_state, fsa, dims, list_of_dict)
        
        path[dim].append(alph)
        state_chain.append(curr_state)
        curr_state = next_state

    return path.values()

def find_edge_earliest(curr_state, fsa, dims, list_of_dict):
    #finding the earliest edge from a given state
    next_state = None
    alph = 'e'
    dim = -1
    rank = 100
    
    outgoing = fsa.edges[curr_state]
    for i in xrange(dims):
        dict_dim = list_of_dict[i]
        for end, tup in outgoing:
            rank_ = dict_dim[tup[i]]
            alph_ = tup[i]
            if rank_ >= 0 and rank_ < rank:
                rank = rank_
                alph = alph_
                dim  = i
                next_state = end
        if alph is not 'e':
            break

    return alph, dim, next_state

def earliest_path(fsa, list_of_dict):
    #designed to handle one initial state
    #list of dict gives the alphabetical order by dimension
    init_state = fsa.init_states[0]
    dims = fsa.dims
    assert len(list_of_dict) == dims

    path = {}
    for i in xrange(dims):
        path[i] = []
    state_chain = []

    curr_state = init_state

    while curr_state not in state_chain and curr_state not in fsa.final_states:
        
        if len(fsa.edges[curr_state]) == 1 and fsa.edges[curr_state][0][1] == tuple(['e']*dims):
            state_chain.append(curr_state)
            curr_state = fsa.edges[curr_state][0][0]
        
        alph, dim, next_state = find_edge_earliest(curr_state, fsa, dims, list_of_dict)
        
        path[dim].append(alph)
        state_chain.append(curr_state)
        curr_state = next_state

    return path.values()

def dep_test(late_path, early_path, dict_alph):
    if len(late_path) is 0 and len(early_path) is 0:
        return None
    if len(late_path) is 0 and len(early_path) is not 0:
        return True
    elif len(late_path) is not 0 and len(early_path) is 0:
        return False
    elif dict_alph[late_path[0]] < dict_alph[early_path[0]]:
        return True 
    elif dict_alph[late_path[0]] > dict_alph[early_path[0]]:
        return False 
    return dep_test(late_path[1:], early_path[1:], dict_alph)

def path_test(late_path, early_path, dict_alph):
    dims = len(dict_alph)
    for i in xrange(dims):
        res = dep_test(late_path[i], early_path[i], dict_alph[i])
        if res is None:
            continue
        else:
            return res

def refine_fsa(fsa):

    n_prev_states = fsa.nstates
    fsa_ = fsa.unreachable_removal()
    n_curr_states = fsa_.nstates

    while n_curr_states is not n_prev_states:
        fsa_ = fsa_.unreachable_removal()
        n_prev_states = n_curr_states
        n_curr_states = fsa_.nstates
    
    return fsa_

def prefix_state_test(dep_fst1, dep_fst2, fst_xform): 
    """
    For a given prefix state checking dependence preservation
    """ 
    #print "\nTransformed Witness Automata 1"
    raw_fsa1 = dep_fst1.compose_fst(fst_xform)
    #raw_fsa1.print_fst()
    raw_fsa1 = raw_fsa1.project_out()
    #print "Raw Automata 1"
    #raw_fsa1.print_fsa()
    tr_dep_fsa1 = refine_fsa(raw_fsa1)
    
    print "\nPre-Suffix x Transform => Project out Automata"
    tr_dep_fsa1.print_fsa()
    #print "\nRank Dictionary Per Dimension"
    rank_dict1 = construct_dict(tr_dep_fsa1.order)
    #print rank_dict1

    l_path = latest_path(tr_dep_fsa1, rank_dict1)
    print "\nLatest Path", l_path

    #print "\nTransformed Witness Automata 2"
    raw_fsa2 = dep_fst2.compose_fst(fst_xform).project_out()
    #print "Raw Automata 2"
    #raw_fsa2.print_fsa()
    tr_dep_fsa2 = refine_fsa(raw_fsa2)
    
    print "\nPost-Suffix x Transform => Project out Automata"
    tr_dep_fsa2.print_fsa()
    #print "\nRank Dictionary Per Dimension"
    rank_dict2 = construct_dict(tr_dep_fsa2.order)
    #print rank_dict2
    
    e_path = earliest_path(tr_dep_fsa2, rank_dict2)
    print "\nEarliest Path", e_path

    #print "\nGlobal Rank Dictionary"
    g_rank_dict = construct_dict(fst_xform.project_out().order)
    #print g_rank_dict

    #print "\nDependence Test: "
    return path_test(l_path, e_path, g_rank_dict)

def is_safe(witness_fsa1, witness_fsa2, fst_xform):
    """
    checking witness tuples on a given xform transducer
    0: <[t1, s1]>
    1: <[r1+t1, s1]>
    2: <[t1, rl2s1]>
    3: <[t1, rr2s1]>
    """
    #print "\nTransformation Transducer"
    #fst_xform.print_fst()
    #print "\nTransformed Witness Automata 1" 
    dep_fst1 = witness_fsa1.identity_fst()
    #print "\nWitness 0"
    #dep_fst1.print_fst()
    #print "\nTransformed Witness Automata 2"
    dep_fst2 = witness_fsa2.identity_fst()
    #print "\nWitness 1"
    #dep_fst2.print_fst()

    prefix_start_states = fst_xform.init_states
    
    if len(prefix_start_states) == 1:

        return prefix_state_test(dep_fst1, dep_fst2, fst_xform)
    
    else:
        for prefix_state in prefix_start_states:
            print "Prefix Start State is ", prefix_state
            fst_xform.init_states = [prefix_state]
            res = prefix_state_test(dep_fst1, dep_fst2, fst_xform)
            if not res:
                fst_xform.init_states = prefix_start_states 
                return False
        
        fst_xform.init_states = prefix_start_states 
        return True

def case_test(case_, fst_xform):
    """
    cases presented in the paper that polyrec handles
    alphabet: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    order   : [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    case 1: n->x[i] = n->x[i] + n->x[i+1]
    case 2: n->x[i] = n->l->x[i] + n->r->x[i]
    case 3: n->x[i] = n->l->x[i+1] + n->r->x[i+1]
    """
    alp    = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    order  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    
    #print "\nWitness Automata <[t1, s1]>"
    fsa0 = MultiTapeFSA(3, [0], [2], 2, alp, order)
    construct_sample_suffix_fsa0(fsa0)
    #fsa0.print_fsa()
    
    #print "\nWitness Automata <[r1+t1, s1]>"
    fsa1 = MultiTapeFSA(4, [0], [3], 2, alp, order)
    construct_sample_suffix_fsa1(fsa1)
    #fsa1.print_fsa()
    
    #print "\nWitness Automata <[r1t1, s1]>"
    fsa2 = MultiTapeFSA(4, [0], [3], 2, alp, order)
    construct_sample_suffix_fsa2(fsa2)
    #fsa1.print_fsa()
    
    #print "\nWitness Automata <[t1, rl2s1]>"
    fsa3 = MultiTapeFSA(4, [0], [3], 2, alp, order)
    construct_sample_suffix_fsa3(fsa3)
    #fsa2.print_fsa()

    #print "\nWitness Automata <t1, rr2s1>"
    fsa4 = MultiTapeFSA(4, [0], [3], 2, alp, order)
    construct_sample_suffix_fsa4(fsa4)
    #fsa3.print_fsa()

    #print "\nWitness Automata <r1t1, rl2s1>"
    fsa5 = MultiTapeFSA(5, [0], [4], 2, alp, order)
    construct_sample_suffix_fsa5(fsa5)
    #fsa4.print_fsa()
    
    #print "\nWitness Automata <r1t1, rr2s1>"
    fsa6 = MultiTapeFSA(5, [0], [4], 2, alp, order)
    construct_sample_suffix_fsa6(fsa6)
    #fsa5.print_fsa()
    
    if case_ is 1:
        result = is_safe(fsa0, fsa1, fst_xform)
        if result:
            print "This x-form is legal for case 1"
        else:
            print "This x-form is legal for case 1"
    elif case_ is 2:
        result = is_safe(fsa3, fsa0, fst_xform) and is_safe(fsa4, fsa0, fst_xform)
        if result:
            print "This x-form is legal for case 2"
        else:
            print "This x-form is illegal for case 2"
    elif case_ is 3:
        result = is_safe(fsa5, fsa2, fst_xform) and is_safe(fsa6, fsa2, fst_xform)
        if result:
            print "This x-form is legal for case 3"
        else:
            print "This x-form is illegal for case 3"
    else:
        print "Error case must be a number between 1 and 3"

def check_ic_cm():

    #print "\nTransform CM(pre)"
    #input alph & ord
    input_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord1  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #output alph & ord
    output_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    output_ord1  = [['e', 't1', 'r1'], ['e', 's1', 'rl2', 'rr2']]
    fst_cm = MultiTapeFST(3, [0], [2], 2, 2, input_alp1, output_alp1, input_ord1, output_ord1)
    construct_fst_lr2lr(fst_cm)
    #fst_cm_pre.print_fst()
    
    #print "\nTransform IC"
    #input alph & ord
    input_alp2  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord2  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #output alph & ord
    output_alp2 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord2 = [['e', 'rl1', 'rr1', 't1'], ['e', 's1', 'r2']]
    fst_ic = MultiTapeFST(3, [0], [2], 2, 2, input_alp2, output_alp2, input_ord2, output_ord2)
    construct_fst_lr2rl(fst_ic)
    #fst_ic.print_fst()

    #print "\n Transform IC-CM(pre)"
    fst_ic_cm = fst_cm.compose_fst(fst_ic)
    #fst_ic_cm.print_fst()

    xforms = [fst_cm, fst_ic, fst_ic_cm]
    names  = ["CM(pre)", "IC", "IC-CM(pre)"]

    #for xf, nm in zip(xforms, names):
    #    for i in xrange(1,4):
    #        print "xform: ", nm
    #        case_test(i, xf)
    case_test(3, fst_ic)

def check_il():
    
    #print "\nTransform CM(pre)"
    #input alph & ord
    input_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord1  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #output alph & ord
    output_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    output_ord1  = [['e', 't1', 'r1'], ['e', 's1', 'rl2', 'rr2']]
    fst_cm = MultiTapeFST(3, [0], [2], 2, 2, input_alp1, output_alp1, input_ord1, output_ord1)
    construct_fst_lr2lr(fst_cm)
    #fst_cm.print_fst()

    #print "\nTransform IL(l)"
    input_alp2  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord2  = [['e', 't1', 'r1'], ['e', 's1', 'rl2', 'rr2']]
    #output alph & ord
    output_alp2  = [['e', 'r1', 't1'], ['e', 'rll2', 'rlr2', 'rr2', 's1', 's2']]
    output_ord2  = [['e', 't1', 'r1'], ['e', 's1', 's2', 'rll2', 'rlr2', 'rr2']]
    fst_ill = MultiTapeFST(6, [0, 3], [2, 5], 2, 2, input_alp2, output_alp2, input_ord2, output_ord2)
    construct_fst_il_llr(fst_ill)
    fst_ill.print_fst()

    #print "\nTransform IL(r)"
    input_alp3  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord3  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #output alph & ord
    output_alp3  = [['e', 'r1', 't1'], ['e', 'rl2', 'rrl2', 'rrr2', 's1', 's2']]
    output_ord3  = [['e', 't1', 'r1'], ['e', 'rl2', 'rrl2', 'rrr2', 's2', 's1']]
    fst_ilr = MultiTapeFST(6, [0, 3], [2, 5], 2, 2, input_alp3, output_alp3, input_ord3, output_ord3)
    construct_fst_il_lrr(fst_ilr)
    #fst_ilr.print_fst()

    #print "\nTransform IL(l)-CM(pre)"
    fst_il_cm = fst_cm.compose_fst(fst_ill)
    #fst_il_cm.print_fst()

    xforms = [fst_cm, fst_ill, fst_il_cm, fst_ilr]
    names  = ["CM(pre)", "IL(l)", "IL(l)-CM(pre)", "IL(r)"]

    for xf, nm in zip(xforms, names):
        for i in xrange(1,5):
            print "xform: ", nm
            case_test(i, xf)
    #case_test(3, fst_ilr)

def check_sm():
    #input alph & ord
    input_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord1  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #output alph & ord
    output_alp1  = [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    output_ord1  = [['e', 't1', 'r1'], ['e', 't2', 'r2'], ['e', 's1', 'rl3', 'rr3']]
    fst_sm = MultiTapeFST(12, [0, 1, 8, 10], [3, 7, 11], 2, 3, input_alp1, output_alp1, input_ord1, output_ord1)
    construct_fst_lr2llr(fst_sm)
    #print "\nSM"
    #fst_sm.print_fst()

    
    #input alph & ord
    input_alp2  = [['e', 'r1', 't1'], ['e', 'r2', 't2'], ['e', 'rl3', 'rr3', 's1']]
    input_ord2  = [['e', 't1', 'r1'], ['e', 't2', 'r2'], ['e', 'rl3', 'rr3', 's1']]
    #output alph & ord
    output_alp2 = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 't2'], ['e', 'r3', 's1']]
    output_ord2 = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 't2'], ['e', 's1', 'r3']]
    #fst_ic = MultiTapeFST(4, [0], [3], 3, 3, input_alp2, output_alp2, input_ord2, output_ord2)
    #construct_fst_llr2lrl(fst_ic)
    #fst_ic.print_fst()

    #fst_ic_sm = fst_sm.compose_fst(fst_ic)
    #fst_ic_sm.print_fst()

    #case_test(1, fst_sm)
    alp    = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    order  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    fsa0 = MultiTapeFSA(3, [0], [2], 2, alp, order)
    construct_sample_suffix_fsa0(fsa0)
    dep_fst1 = fsa0.identity_fst()
    dep_fsa1 = dep_fst1.compose_fst(fst_sm).project_out()
    prefix_init_states = dep_fsa1.init_states
    for i in prefix_init_states:
        print "For init state ", i
        dep_fsa1.init_states = tuple([i])
        refine_fsa(dep_fsa1).print_fsa()

def case01(fst, xform_name):
    
    #alp    = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    #order  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    #prog = MultiTapeFSA(3, [0], [2], 2, alp, order)
    #simple_prog(prog)

    #print "\nProgram Automata"
    #prog.print_fsa()

    #xform = prog.identity_fst().compose_fst(fst)
    xform = fst
    
    #print "\nProgram x Transformation Transducer"
    #xform.print_fst()

    fsa0 = MultiTapeFSA(3, [0], [2], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa0(fsa0) 

    print "\nSuffix 1 Automata"
    fsa0.print_fsa()
    
    fsa1 = MultiTapeFSA(4, [0], [3], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa1(fsa1)

    print "\nSuffix 2 Automata"
    fsa1.print_fsa()

    if is_safe(fsa0, fsa1, xform):
        print xform_name, " is sound for case01"
    else:
        print xform_name, " is unsound for case01"

def case02(fst, xform_name):
    
    xform = fst
    
    fsa0 = MultiTapeFSA(3, [0], [2], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa0(fsa0)

    print "\nSuffix 1 Automata"
    fsa0.print_fsa()
    
    fsa3 = MultiTapeFSA(4, [0], [3], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa3(fsa3)

    print "\nSuffix 2_1 Automata"
    fsa3.print_fsa()

    fsa4 = MultiTapeFSA(4, [0], [3], 2, xform.alphabet_in, xform.ord_in) 
    construct_sample_suffix_fsa4(fsa4)

    print "\nSuffix 2_2 Automata" 
    fsa4.print_fsa()
    
    if is_safe(fsa3, fsa0, xform) and is_safe(fsa4, fsa0, xform):
        print xform_name, " is sound for case02"
    else:
        print xform_name, "is unsound for case02"

def case03(fst, xform_name):
    
    xform = fst
    
    fsa2 = MultiTapeFSA(4, [0], [3], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa2(fsa2)
    
    fsa5 = MultiTapeFSA(5, [0], [4], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa5(fsa5)
    
    fsa6 = MultiTapeFSA(5, [0], [4], 2, xform.alphabet_in, xform.ord_in)
    construct_sample_suffix_fsa6(fsa6)

    if is_safe(fsa5, fsa2, xform) and is_safe(fsa6, fsa2, xform):
        print xform_name, " is sound for case03"
    else:
        print xform_name, " is unsound for case03"

def partial_case03(partial_fst):
    alp    = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    order  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    prog = MultiTapeFSA(3, [0], [2], 2, alp, order)
    simple_prog(prog)

    xform_partial = prog.identity_fst().compose_fst(partial_fst)

    input_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord1  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    output_alp1 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord1 = [['e', 'rl1', 'rr1', 't1'], ['e', 's1', 'r2']]

    fst_ic1 = MultiTapeFST(3, [0], [2], 2, 2, input_alp1, output_alp1, input_ord1, output_ord1)
    construct_fst_lr2rl(fst_ic1)

    input_alp2  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord2  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    output_alp2 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord2 = [['e', 't1', 'rl1', 'rr1'], ['e', 's1', 'r2']]

    fst_ic2 = MultiTapeFST(3, [0], [2], 2, 2, input_alp2, output_alp2, input_ord2, output_ord2)
    construct_fst_lr2rl(fst_ic2)

    input_alp3  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord3  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    output_alp3 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord3 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]

    fst_ic3 = MultiTapeFST(3, [0], [2], 2, 2, input_alp3, output_alp3, input_ord3, output_ord3)
    construct_fst_lr2rl(fst_ic3)

    input_alp4  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord4  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    output_alp4 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord4 = [['e', 't1', 'rl1', 'rr1'], ['e', 'r2', 's1']]

    fst_ic4 = MultiTapeFST(3, [0], [2], 2, 2, input_alp4, output_alp4, input_ord4, output_ord4)
    construct_fst_lr2rl(fst_ic4)

    completion_fst = [fst_ic4, fst_ic2, fst_ic3, fst_ic1]
    completion_name = ["ic4", "ic2", "ic3", "ic1"]

    fsa2 = MultiTapeFSA(4, [0], [3], 2, alp, order)
    construct_sample_suffix_fsa2(fsa2)
    
    fsa5 = MultiTapeFSA(5, [0], [4], 2, alp, order)
    construct_sample_suffix_fsa5(fsa5)
    
    fsa6 = MultiTapeFSA(5, [0], [4], 2, alp, order)
    construct_sample_suffix_fsa6(fsa6)

    for fst, name in zip(completion_fst, completion_name):
        xform_full = xform_partial.compose_fst(fst)
        if is_safe(fsa5, fsa2, xform_full) and is_safe(fsa6, fsa2, xform_full):
            print name, " completes the partial transformation"
    
    
if __name__ == "__main__":

    input_alp1  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord1  = [['e', 't1', 'r1'], ['e', 'rl2', 'rr2', 's1']]
    output_alp1 = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    output_ord1 = [['e', 't1', 'r1'], ['e', 's1', 'rl2', 'rr2']]

    fst_cm = MultiTapeFST(3, [0], [2], 2, 2, input_alp1, output_alp1, input_ord1, output_ord1)
    construct_fst_lr2lr(fst_cm)
    
    input_alp2  = [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    input_ord2  = [['e', 't1', 'r1'], ['e', 's1', 'rl2', 'rr2']]
    output_alp2 = [['e', 'rl1', 'rr1', 't1'], ['e', 'r2', 's1']]
    output_ord2 = [['e', 't1', 'rl1', 'rr1'], ['e', 's1', 'r2']]

    fst_ic = MultiTapeFST(3, [0], [2], 2, 2, input_alp2, output_alp2, input_ord2, output_ord2)
    construct_fst_lr2rl(fst_ic)

    #fst_ic_cm = fst_cm.compose_fst(fst_ic)

    print "Transformation Transducer"
    fst_ic.print_fst()
    
    print "\n\nCase 01"
    #case01(fst_cm, "Code Motion (Post - Pre)")
    case01(fst_ic, "Interchange")
    #case01(fst_ic_cm, "CM then IC")
    
    print "\n\nCase 02"
    #case02(fst_cm, "Code Motion (Post - Pre)")
    case02(fst_ic, "Interchange")
    #case02(fst_ic_cm, "CM then IC")
   
    print "\n\nCase 03"
    #case03(fst_cm, "Code Motion (Post - Pre)")
    case03(fst_ic, "Interchange")
    #case03(fst_ic_cm, "CM then IC")

    #print "Completion Procedure"
    #partial_case03(fst_cm)


    