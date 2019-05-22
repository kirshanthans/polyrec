import sys, os
from statemachines import MultiTapeFSA, MultiTapeFST

class Transformation:
    def __init__(self, *args, **kwargs):
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

                fst.add_transition(s+d, s+d+1, tuple(tup_in), tuple(tup_out)


