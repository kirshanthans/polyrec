#!/usr/bin/python
import sys, os

class MultiTapeFSA:
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

    def copy(self):

        fsa = MultiTapeFSA(self.nstates, self.init_states, self.final_states, self.dims, self.alphabet, self.order)

        for s, e, tup in self.transitions:
            fsa.add_transition(s, e, tup) 

        return fsa
   
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

    def print_prog(self):

        for i in xrange(self.dims):
            print "Dim ", i
            for label in self.order[i][1:]:
                print "\t", label

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

    @staticmethod
    def refine_fsa(fsa):

        n_prev_states = fsa.nstates
        fsa_ = fsa.unreachable_removal()
        n_curr_states = fsa_.nstates

        while n_curr_states is not n_prev_states:
            fsa_ = fsa_.unreachable_removal()
            n_prev_states = n_curr_states
            n_curr_states = fsa_.nstates

        return fsa

class MultiTapeFST:
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
