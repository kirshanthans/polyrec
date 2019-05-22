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

def cm_fst(fst, dim, dim_type):
    """
    fst: MultitapeFST
    dim: # Dimensions
    dim_type: List of size <dim>. dim_type[i] is # calls in ith dimension
    """
    assert dim == len(dim_type)
    assert dim+1 == fst.nstates

    in_alph  = fst.alphabet_in
    out_alph = fst.alphabet_out

    assert len(in_alph) == len(out_alph)
    #call statements
    for i in xrange(dim):
        for j in xrange(dim_type[i]):
            tup_in  = ['e'] * dim 
            tup_out = ['e'] * dim
            
            tup_in[i]  = in_alph[i][j+1] 
            tup_out[i] = out_alph[i][j+1] 
            
            fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))
    #transfer-compute statements
    for i in xrange(dim):
        tup_in  = ['e'] * dim 
        tup_out = ['e'] * dim
        
        tup_in[i] = in_alph[i][dim_type[i]+1]
        tup_out[i] = out_alph[i][dim_type[i]+1]
        
        fst.add_transition(i, i+1, tuple(tup_in), tuple(tup_out))

def code_motion(in_dim, out_dim, in_dim_type, out_dim_type, in_alp, out_alp, in_ord, out_ord):
    
    assert in_dim == out_dim
    assert in_dim_type == out_dim_type
    assert in_dim == len(in_alp)
    assert in_dim == len(in_ord)
    assert out_dim == len(out_alp)
    assert out_dim == len(out_ord)

    dim = in_dim
    dim_type = in_dim_type

    fst = MultiTapeFST(dim+1, [0], [dim], dim, dim, in_alp, out_alp, in_ord, out_ord)
    cm_fst(fst, dim, dim_type)

    return fst

def ic_fst(fst, dim, in_dim_type, out_dim_type, dim_i1, dim_i2):
    """
    fst: MultitapeFST
    dim: # Dimensions
    in_dim_type: List of size <dim>. dim_type[i] is # calls in ith dimension of the input tape
    out_dim_type: List of size <dim>. dim_type[i] is # calls in ith dimension of the output tape
    dim_i1, dim_i2: dimensions of interchange
    """
    assert dim+1 == fst.nstates

    in_alph  = fst.alphabet_in
    out_alph = fst.alphabet_out

    assert len(in_alph) == len(out_alph)

    for i in xrange(dim):
        if i is not dim_i1 or i is not dim_i2:
            for j in xrange(in_dim_type[i]):
                tup_in  = ['e'] * dim 
                tup_out = ['e'] * dim
                
                tup_in[i]  = in_alph[i][j+1]
                tup_out[i] = out_alph[i][j+1]
                
                fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))
    
    calls_i1 = in_dim_type[dim_i1]
    calls_i2 = in_dim_type[dim_i2]
    
    in_label_i1 = in_alph[dim_i1][1:1+calls_i1]
    in_label_i2 = in_alph[dim_i2][1:1+calls_i2]

    out_label_i1 = out_alph[dim_i2][1:1+calls_i1]
    out_label_i2 = out_alph[dim_i1][1:1+calls_i2]

    assert len(in_label_i1) == len(out_label_i1)
    assert len(in_label_i2) == len(out_label_i2)

    for in_l, out_l in zip(in_label_i1, out_label_i1):        
        tup_in  = ['e'] * dim 
        tup_out = ['e'] * dim

        tup_in[dim_i1] = in_l
        tup_out[dim_i2] = out_l
        
        fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))
    
    for in_l, out_l in zip(in_label_i2, out_label_i2):        
        tup_in  = ['e'] * dim 
        tup_out = ['e'] * dim

        tup_in[dim_i2] = in_l
        tup_out[dim_i1] = out_l

        fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))

    for i in xrange(dim):
        tup_in  = ['e'] * dim 
        tup_out = ['e'] * dim
        
        tup_in[i] = in_alph[i][in_dim_type[i]+1]
        tup_out[i] = out_alph[i][out_dim_type[i]+1]
        
        fst.add_transition(i, i+1, tuple(tup_in), tuple(tup_out))

def interchange(in_dim, out_dim, in_dim_type, out_dim_type, in_alp, out_alp, in_ord, out_ord, dim_i1, dim_i2):
    
    assert in_dim == out_dim
    assert in_dim == len(in_alp)
    assert in_dim == len(in_ord)
    assert out_dim == len(out_alp)
    assert out_dim == len(out_ord)
    assert dim_i1 + 1 == dim_i2

    dim = in_dim
    
    fst = MultiTapeFST(dim+1, [0], [dim], dim, dim, in_alp, out_alp, in_ord, out_ord)
    ic_fst(fst, dim, in_dim_type, out_dim_type, dim_i1, dim_i2)

    return fst

def il_fst(fst, dim, in_dim_type, out_dim_type, dim_inline, il_call_label, il_d_in_call_labels, il_d_out_call_labels, stmt_label, il_d_out_stmt_labels):
    
    assert len(il_d_in_call_labels) == len(il_d_out_call_labels)
    assert len(il_d_out_stmt_labels) == 2

    in_alph = fst.alphabet_in
    out_alph = fst.alphabet_out

    for i in xrange(dim):
        if i is not dim_inline:
            for j in xrange(in_dim_type[i]):
                tup_in  = ['e'] * dim 
                tup_out = ['e'] * dim
            
                tup_in[i]  = in_alph[i][j+1] 
                tup_out[i] = out_alph[i][j+1] 
            
                fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))
                fst.add_transition(dim+1, dim+1, tuple(tup_in), tuple(tup_out))
    
    for i in xrange(dim):
        if i is not dim_inline:
            tup_in  = ['e'] * dim 
            tup_out = ['e'] * dim
        
            tup_in[i] = in_alph[i][in_dim_type[i]+1]
            tup_out[i] = out_alph[i][in_dim_type[i]+1]
        
            fst.add_transition(i, i+1, tuple(tup_in), tuple(tup_out))
            fst.add_transition((dim+1)+i, (dim+1)+i+1, tuple(tup_in), tuple(tup_out))

    tup_in = ['e'] * dim
    tup_out = ['e'] * dim
    tup_in[dim_inline] = il_call_label
    fst.add_transition(0, dim+1, tuple(tup_in), tuple(tup_out))

    for in_l, out_l in zip(il_d_in_call_labels, il_d_out_call_labels):
        tup_in = ['e'] * dim
        tup_out = ['e'] * dim

        tup_in[dim_inline] = in_l
        tup_out[dim_inline] = out_l
        
        fst.add_transition(dim+1, 0, tuple(tup_in), tuple(tup_out))

    out_stmt1, out_stmt2 = il_d_out_stmt_labels
    
    tup_in = ['e'] * dim
    tup_out = ['e'] * dim
    tup_in[dim_inline] = stmt_label
    tup_out[dim_inline] = out_stmt1
    fst.add_transition(dim_inline, dim_inline+1, tuple(tup_in), tuple(tup_out))
    
    tup_in = ['e'] * dim
    tup_out = ['e'] * dim
    tup_in[dim_inline] = stmt_label
    tup_out[dim_inline] = out_stmt2
    fst.add_transition((dim+1)+dim_inline, (dim+1)+dim_inline+1, tuple(tup_in), tuple(tup_out))

def inlining(in_dim, out_dim, in_dim_type, in_alp, in_ord, dim_inline, call_inline, label):
    #inlining only one call at once
    assert in_dim == out_dim
    assert in_dim == len(in_alp)
    assert in_dim == len(in_ord)
    #assert dim_inline == in_dim-1
    assert call_inline < in_dim_type[dim_inline]+1 and call_inline > 0

    dim = in_dim
    # concstruct output alphabet and order
    # -- alphabet
    # number of calls in inlining dim
    ncalls = in_dim_type[dim_inline]
    # all call labels in inlining dim
    il_d_in_call_labels = in_alp[dim_inline][1:1+ncalls]
    # label of the call getting inlined
    il_call_label = in_alp[dim_inline][call_inline]
    # all other call labels
    other_call_labels = [l for l in il_d_in_call_labels if l is not il_call_label]
    # label of compute statements
    stmt_label  = in_alp[dim_inline][1+ncalls]

    # output labels of calls
    new_call_labels = [l+label for l in il_d_in_call_labels]
    il_d_out_call_labels = new_call_labels + other_call_labels
    # output labels of statements
    il_d_out_stmt_labels = [stmt_label, stmt_label+label] 
    # output labels for the dim getting inlined
    il_d_alp = ['e'] + il_d_out_call_labels + il_d_out_stmt_labels
    
    # output alphabet
    out_alp = []
    for i in xrange(dim):
        if i is not dim_inline:
            out_alp.append(in_alp[i])
        else:
            out_alp.append(il_d_alp)
    # -- order
    # output order of labels replacing the call that getting inlined 
    il_d_call_label_rep = [l+label for l in in_ord[dim_inline][1:]]
    # output order of the dim getting inlined
    il_d_ord = []
    for l in in_ord[dim_inline]:
        if l is not il_call_label:
            il_d_ord.append(l)
        else:
            il_d_ord += il_d_call_label_rep
    
    # output order
    out_ord = []
    for i in xrange(dim):
        if i is not dim_inline:
            out_ord.append(in_alp[i])
        else:
            out_ord.append(il_d_ord)

    fst = MultiTapeFST(2*(dim+1), [0, dim+1], [dim, 2*dim+1], dim, dim, in_alp, out_alp, in_ord, out_ord)

    out_dim_type = list(in_dim_type)
    out_dim_type[dim_inline] = len(il_d_out_call_labels)
    
    il_fst(fst, dim, in_dim_type, out_dim_type, dim_inline, il_call_label, il_d_in_call_labels, new_call_labels, stmt_label, il_d_out_stmt_labels)

    return fst

def sm_fst(fst, in_dim, out_dim, in_dim_type, dim_strip, strip_size):

    in_alp  = fst.alphabet_in
    out_alp = fst.alphabet_out
    in_ord  = fst.ord_in
    out_ord = fst.ord_out

    n = fst.nstates

    for s in xrange(0, n, out_dim+1):
        for d in xrange(in_dim):
            if d is dim_strip:
                #call statement of stripped dimensions
                if (s+out_dim+1) < n:
                    tup_in  = ['e'] * in_dim
                    tup_out = ['e'] * out_dim
                    
                    tup_in[d]  = in_alp[d][1]
                    tup_out[d+1] = out_alp[d+1][1]

                    fst.add_transition(s, s+out_dim+1, tuple(tup_in), tuple(tup_out))

            elif d < dim_strip:
                #call statements non-stripped dimensions
                for j in xrange(in_dim_type[d]):
                    tup_in  = ['e'] * in_dim
                    tup_out = ['e'] * out_dim
                    
                    tup_in[d]  = in_alp[d][j+1]
                    tup_out[d] = out_alp[d][j+1]

                    fst.add_transition(s, s, tuple(tup_in), tuple(tup_out))

            elif d > dim_strip:
                #call statements non-stripped dimensions
                for j in xrange(in_dim_type[d]):
                    tup_in  = ['e'] * in_dim
                    tup_out = ['e'] * out_dim
                    
                    tup_in[d]  = in_alp[d][j+1]
                    tup_out[d+1] = out_alp[d+1][j+1]

                    fst.add_transition(s, s, tuple(tup_in), tuple(tup_out))
        
        #new dimension transfer call
        tup_in  = ['e'] * in_dim
        tup_out = ['e'] * out_dim
        
        tup_out[dim_strip] = out_alp[dim_strip][2]
                    
        fst.add_transition(s, s+1, tuple(tup_in), tuple(tup_out))

    
    #call statement of new dimension
    tup_in  = ['e'] * in_dim
    tup_out = ['e'] * out_dim
    
    tup_out[dim_strip] = out_alp[dim_strip][1]

    fst.add_transition(n-out_dim-1, 0, tuple(tup_in), tuple(tup_out))

    #existing transfer statements
    for s in xrange(1, n, out_dim+1):
        for d in xrange(in_dim):
            tup_in  = ['e'] * in_dim
            tup_out = ['e'] * out_dim
            if d < dim_strip:
                tup_in[d]  = in_alp[d][in_dim_type[d]+1]
                tup_out[d] = out_alp[d][in_dim_type[d]+1]
            elif d >= dim_strip:
                tup_in[d]    = in_alp[d][in_dim_type[d]+1]
                tup_out[d+1] = out_alp[d+1][in_dim_type[d]+1]

            fst.add_transition(s+d, s+d+1, tuple(tup_in), tuple(tup_out))

def shift_dim(alp, odr, from_dim, to_dim):
    n_alp = ['e']
    n_odr = ['e']

    to_dim_id = to_dim + 1
    for a in alp[1:]:
        if a[0] is not 's':
            n_a = a[0] + str(to_dim_id) + a[2:]
        else:
            n_a = str(a)
        n_alp.append(n_a)
    
    for o in odr[1:]:
        if o[0] is not 's':
            n_o = o[0] + str(to_dim_id) + o[2:]
        else:
            n_o = str(o)
        n_odr.append(n_o)

    return n_alp, n_odr

def strip_mining(in_dim, out_dim, in_dim_type, in_alp, in_ord, dim_strip, strip_size):

    assert in_dim_type[dim_strip] == 1
    assert in_dim + 1 == out_dim

    n_states = (strip_size+1)*(out_dim+1)
    init = range(0, n_states, out_dim+1) + range(1, n_states, out_dim+1)
    init.sort()
    final = range(out_dim, n_states, out_dim+1)
    
    out_alp = [alp for alp in in_alp[:dim_strip]]
    out_ord = [odr for odr in in_ord[:dim_strip]]
    
    new_dim_id = dim_strip + 1
    new_dim_alp = ['e', 'r'+str(new_dim_id), 't'+str(new_dim_id)]
    new_dim_ord = ['e']
    if in_alp[dim_strip] != in_ord[dim_strip]:
        new_dim_ord.append('t'+str(new_dim_id))
        new_dim_ord.append('r'+str(new_dim_id))
    else:
        new_dim_ord.append('r'+str(new_dim_id))
        new_dim_ord.append('t'+str(new_dim_id))

    out_alp.append(new_dim_alp)
    out_ord.append(new_dim_ord)

    for i in xrange(dim_strip, in_dim):
        alp, odr = shift_dim(in_alp[i], in_ord[i], i, i+1)
        out_alp.append(alp)
        out_ord.append(odr)

    fst = MultiTapeFST(n_states, init, final, in_dim, out_dim, in_alp, out_alp, in_ord, out_ord)
    sm_fst(fst, in_dim, out_dim, in_dim_type, dim_strip, strip_size)
    
    return fst
# On each dimension alphabet is organized as
# <epsilon - calls - transfer or compute statement>
# Label 'e' is reserved for epsilon
# Calls are of the format r<dim><label>
# Transfer statements are of the format t<dim>
# Compute statement is usually s1. If incremented then goes on as s2, s3 etc.

def cm_test():
    print "Code Motion Test"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    out_dim_type = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # Output alphabet and order
    out_alp = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    fst = code_motion(in_dim, out_dim, in_dim_type, out_dim_type, in_alp, out_alp, in_ord, out_ord)
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()

def ic_test():
    print "Interchange Test"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    out_dim_type = [2, 1]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]
    # Output alphabet and order
    out_alp = [['e', 'r1l', 'r1r', 't1'], ['e', 'r2', 's1']]
    out_ord = [['e', 't1', 'r1l', 'r1r'], ['e', 's1', 'r2']]

    fst = interchange(in_dim, out_dim, in_dim_type, out_dim_type, in_alp, out_alp, in_ord, out_ord, 0, 1)
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()

def il_test():
    print "Inlining Test"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    fst = inlining(in_dim, out_dim, in_dim_type, in_alp, in_ord, 1, 1, 'l')
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()
    fst = inlining(in_dim, out_dim, in_dim_type, in_alp, in_ord, 1, 2, 'r')
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()
    fst = inlining(in_dim, out_dim, in_dim_type, in_alp, in_ord, 0, 1, 'n')
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()

def sm_test():
    print "Strip-Mining Test1"
    # Dimensions
    in_dim  = 2
    out_dim = 3
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # strip dimension 
    strip_dim  = 0
    # strip size
    strip_size = 2

    fst = strip_mining(in_dim, out_dim, in_dim_type, in_alp, in_ord, strip_dim, strip_size)
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog() 
    
    print "\nStrip-Mining Test2"
    # Dimensions
    in_dim  = 2
    out_dim = 3
    # Type of dimensions
    in_dim_type  = [2, 1]
    # Input alphabet and order
    in_alp  = [['e', 'r1l', 'r1r', 't1'], ['e', 'r2', 's1']]
    in_ord  = [['e', 'r1l', 'r1r', 't1'], ['e', 's1', 'r2']]
    # strip dimension 
    strip_dim  = 1
    # strip size
    strip_size = 2

    fst = strip_mining(in_dim, out_dim, in_dim_type, in_alp, in_ord, strip_dim, strip_size)
    print "\nInput Program"
    prog_in = fst.project_in()
    prog_in.print_prog()
    print "\nOutput Program"
    prog_out = fst.project_out()
    prog_out.print_prog()

if __name__ == "__main__":
    sm_test()

