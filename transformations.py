#!/usr/bin/python
import sys, os
from statemachines import MultiTapeFSA, MultiTapeFST

class Transformation:
    def __init__(self, **kwargs):
        self.name        = kwargs.get('name')
        self.in_dim      = kwargs.get('in_dim')
        self.out_dim     = kwargs.get('out_dim')
        self.in_dim_type = kwargs.get('in_dim_type')
        self.in_alp      = kwargs.get('in_alp')
        self.in_ord      = kwargs.get('in_ord')
        
        self.fst = None
        
        if self.name is 'cm':
            self.out_dim_type = kwargs.get('out_dim_type')
            self.out_alp = kwargs.get('out_alp')
            self.out_ord = kwargs.get('out_ord')
            
            self.fst = Transformation.code_motion(
                in_dim       = self.in_dim,
                out_dim      = self.out_dim,
                in_dim_type  = self.in_dim_type,
                out_dim_type = self.out_dim_type,
                in_alp       = self.in_alp,
                out_alp      = self.out_alp,
                in_ord       = self.in_ord,
                out_ord      = self.out_ord)
        
        elif self.name is 'ic':
            
        elif self.name is 'il':
            pass
        elif self.name is 'sm':
            pass
        else:
            assert False
    
    def input_program(self):
        print "\nInput Program"
        self.fst.project_in().print_fsa()
    
    def output_program(self):
        print "\nOutput Program"
        self.fst.project_out().print_fsa()

    def compose(self, xform):
        pass

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
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

        return n_alp, n_od

    @staticmethod
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
        Transformation.cm_fst(fst, dim, dim_type)

        return fst

    @staticmethod
    def interchange(in_dim, out_dim, in_dim_type, out_dim_type, in_alp, out_alp, in_ord, out_ord, dim_i1, dim_i2):

        assert in_dim == out_dim
        assert in_dim == len(in_alp)
        assert in_dim == len(in_ord)
        assert out_dim == len(out_alp)
        assert out_dim == len(out_ord)
        assert dim_i1 + 1 == dim_i2

        dim = in_dim

        fst = MultiTapeFST(dim+1, [0], [dim], dim, dim, in_alp, out_alp, in_ord, out_ord)
        Transformation.ic_fst(fst, dim, in_dim_type, out_dim_type, dim_i1, dim_i2)

        return fst
    
    @staticmethod
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

        Transformation.il_fst(fst, dim, in_dim_type, out_dim_type, dim_inline, il_call_label, il_d_in_call_labels, new_call_labels, stmt_label, il_d_out_stmt_labels)

        return fst
    
    @staticmethod
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
            alp, odr = Transformation.shift_dim(in_alp[i], in_ord[i], i, i+1)
            out_alp.append(alp)
            out_ord.append(odr)

        fst = MultiTapeFST(n_states, init, final, in_dim, out_dim, in_alp, out_alp, in_ord, out_ord)
        Transformation.sm_fst(fst, in_dim, out_dim, in_dim_type, dim_strip, strip_size)

        return fst

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

    xform = Transformation(
        name         ='cm',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        out_dim_type = out_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        out_alp      = out_alp,
        out_ord      = out_ord)

    xform.input_program()
    xform.output_program()   

if __name__ == "__main__":
    cm_test()
