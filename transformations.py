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
        
        if self.name == 'cm':
            self.out_ord      = kwargs.get('out_ord')
            
            self.fst, self.out_dim_type, self.out_alp = Transformation.code_motion(
                in_dim       = self.in_dim,
                out_dim      = self.out_dim,
                in_dim_type  = self.in_dim_type,
                in_alp       = self.in_alp,
                in_ord       = self.in_ord,
                out_ord      = self.out_ord)
        
        elif self.name == 'ic':
            dim_i1            = kwargs.get('dim_i1')
            dim_i2            = kwargs.get('dim_i2')

            self.fst, self.out_dim_type, self.out_alp, self.out_ord = Transformation.interchange(
                in_dim       = self.in_dim,
                out_dim      = self.out_dim,
                in_dim_type  = self.in_dim_type,
                in_alp       = self.in_alp,
                in_ord       = self.in_ord,
                dim_i1       = dim_i1,
                dim_i2       = dim_i2)
        
        elif self.name == 'il':
            dim_inline  = kwargs.get('dim_inline')
            call_inline = kwargs.get('call_inline')
            label       = kwargs.get('label')

            self.fst, self.out_dim_type, self.out_alp, self.out_ord = Transformation.inlining(
                in_dim      = self.in_dim,
                out_dim     = self.out_dim,
                in_dim_type = self.in_dim_type,
                in_alp      = self.in_alp,
                in_ord      = self.in_ord,
                dim_inline  = dim_inline,
                call_inline = call_inline,
                label       = label)
        
        elif self.name == 'sm':
            dim_strip  = kwargs.get('dim_strip')
            strip_size = kwargs.get('strip_size')
            
            self.fst, self.out_dim_type, self.out_alp, self.out_ord = Transformation.strip_mining(
                in_dim      = self.in_dim,
                out_dim     = self.out_dim,
                in_dim_type = self.in_dim_type,
                in_alp      = self.in_alp,
                in_ord      = self.in_ord,
                dim_strip   = dim_strip,
                strip_size  = strip_size)
        
        else:
            self.out_dim_type = kwargs.get('out_dim_type')
            self.out_alp      = kwargs.get('out_alp')
            self.out_ord      = kwargs.get('out_ord')
            self.fst          = kwargs.get('fst')
    
    def input_program(self):
        print "\nInput Program"
        self.fst.project_in().print_prog()
    
    def output_program(self):
        print "\nOutput Program"
        self.fst.project_out().print_prog()

    def compose(self, xform):
        assert self.out_dim == xform.in_dim
        assert self.out_dim_type == xform.in_dim_type
        assert self.out_alp == xform.in_alp 
        assert self.out_ord == xform.in_ord

        comp_xform = Transformation(
            name         = self.name + '-' + xform.name,
            in_dim       = self.in_dim,
            out_dim      = xform.out_dim,
            in_dim_type  = self.in_dim_type,
            out_dim_type = xform.out_dim_type,
            in_alp       = self.in_alp,
            out_alp      = xform.out_alp,
            in_ord       = self.in_ord,
            out_ord      = xform.out_ord,
            fst          = self.fst.compose_fst(xform.fst))

        return comp_xform

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
            if i != dim_i1 or i != dim_i2:
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
            if i != dim_inline:
                for j in xrange(in_dim_type[i]):
                    tup_in  = ['e'] * dim 
                    tup_out = ['e'] * dim

                    tup_in[i]  = in_alph[i][j+1] 
                    tup_out[i] = out_alph[i][j+1] 

                    fst.add_transition(0, 0, tuple(tup_in), tuple(tup_out))
                    fst.add_transition(dim+1, dim+1, tuple(tup_in), tuple(tup_out))
    
        for i in xrange(dim):
            if i != dim_inline:
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
                if d == dim_strip:
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
            if a[0] != 's':
                n_a = a[0] + str(to_dim_id) + a[2:]
            else:
                n_a = str(a)
            n_alp.append(n_a)

        for o in odr[1:]:
            if o[0] != 's':
                n_o = o[0] + str(to_dim_id) + o[2:]
            else:
                n_o = str(o)
            n_odr.append(n_o)

        return n_alp, n_odr

    @staticmethod
    def swap_symbol(alp, odr, e_symbol, n_symbol):
        n_alp = list(alp)
        n_odr = list(odr)

        n = len(alp)

        for i in xrange(n):
            if n_alp[i] == e_symbol:
                n_alp[i] = n_symbol
            if n_odr[i] == e_symbol:
                n_odr[i] = n_symbol
        
        return n_alp, n_odr

    @staticmethod
    def code_motion(in_dim, out_dim, in_dim_type, in_alp, in_ord, out_ord):

        assert in_dim == out_dim
        assert in_dim == len(in_alp)
        assert in_dim == len(in_ord)
        assert out_dim == len(out_ord)

        dim = in_dim
        dim_type = in_dim_type

        out_dim_type = list(in_dim_type)
        out_alp = list(in_alp)

        fst = MultiTapeFST(dim+1, [0], [dim], dim, dim, in_alp, in_alp, in_ord, out_ord)
        Transformation.cm_fst(fst, dim, dim_type)

        return fst, out_dim_type, out_alp

    @staticmethod
    def interchange(in_dim, out_dim, in_dim_type, in_alp, in_ord, dim_i1, dim_i2):

        assert in_dim == out_dim
        assert in_dim == len(in_alp)
        assert in_dim == len(in_ord)
        assert dim_i1 + 1 == dim_i2

        dim = in_dim
        # constructing the output dimension types
        out_dim_type = list(in_dim_type)
        out_dim_type[dim_i1], out_dim_type[dim_i2] = in_dim_type[dim_i2], in_dim_type[dim_i1]
        # constructing the output alphabet
        alp_dim1, alp_dim2 = in_alp[dim_i1], in_alp[dim_i2]
        ord_dim1, ord_dim2 = in_ord[dim_i1], in_ord[dim_i2]

        out_alp_dim1, out_ord_dim1 = Transformation.shift_dim(alp_dim2, ord_dim2, dim_i2, dim_i1)
        out_alp_dim2, out_ord_dim2 = Transformation.shift_dim(alp_dim1, ord_dim1, dim_i1, dim_i2)

        _out_alp_dim1, _out_ord_dim1 = Transformation.swap_symbol(out_alp_dim1, out_ord_dim1, out_alp_dim1[-1], alp_dim1[-1])
        _out_alp_dim2, _out_ord_dim2 = Transformation.swap_symbol(out_alp_dim2, out_ord_dim2, out_alp_dim2[-1], alp_dim2[-1])

        out_alp, out_ord = list(in_alp), list(in_ord)

        out_alp[dim_i1], out_ord[dim_i1] = _out_alp_dim1, _out_ord_dim1
        out_alp[dim_i2], out_ord[dim_i2] = _out_alp_dim2, _out_ord_dim2

        fst = MultiTapeFST(dim+1, [0], [dim], dim, dim, in_alp, out_alp, in_ord, out_ord)
        Transformation.ic_fst(fst, dim, in_dim_type, out_dim_type, dim_i1, dim_i2)

        return fst, out_dim_type, out_alp, out_ord
    
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
        other_call_labels = [l for l in il_d_in_call_labels if l != il_call_label]
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
            if i != dim_inline:
                out_alp.append(in_alp[i])
            else:
                out_alp.append(il_d_alp)
        # -- order
        # output order of labels replacing the call that getting inlined 
        il_d_call_label_rep = [l+label for l in in_ord[dim_inline][1:]]
        # output order of the dim getting inlined
        il_d_ord = []
        for l in in_ord[dim_inline]:
            if l != il_call_label:
                il_d_ord.append(l)
            else:
                il_d_ord += il_d_call_label_rep

        # output order
        out_ord = []
        for i in xrange(dim):
            if i != dim_inline:
                out_ord.append(in_ord[i])
            else:
                out_ord.append(il_d_ord)

        fst = MultiTapeFST(2*(dim+1), [0, dim+1], [dim, 2*dim+1], dim, dim, in_alp, out_alp, in_ord, out_ord)

        out_dim_type = list(in_dim_type)
        out_dim_type[dim_inline] = len(il_d_out_call_labels)

        Transformation.il_fst(fst, dim, in_dim_type, out_dim_type, dim_inline, il_call_label, il_d_in_call_labels, new_call_labels, stmt_label, il_d_out_stmt_labels)

        return fst, out_dim_type, out_alp, out_ord
    
    @staticmethod
    def strip_mining(in_dim, out_dim, in_dim_type, in_alp, in_ord, dim_strip, strip_size):

        assert in_dim_type[dim_strip] == 1
        assert in_dim + 1 == out_dim

        out_dim_type = list(in_dim_type)
        out_dim_type.insert(dim_strip, 1)

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

        return fst, out_dim_type, out_alp, out_ord

def cm_test():
    print "Code Motion Test"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    # Output order
    out_ord = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    xform = Transformation(
        name         ='cm',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        out_ord      = out_ord)

    xform.input_program()
    xform.output_program()   

def ic_test():
    print "Interchange Test"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    xform = Transformation(
        name         ='ic',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        dim_i1       = 0,
        dim_i2       = 1)

    xform.input_program()
    xform.output_program()  

def il_test():
    print "Inlining Test1"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    xform1 = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 1,
        call_inline = 1,
        label       = 'l')

    xform1.input_program()
    xform1.output_program()
    
    print "\nInlining Test2"
    xform2 = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 1,
        call_inline = 2,
        label       = 'r')

    xform2.input_program()
    xform2.output_program()
    
    print "\nInlining Test3"
    xform3 = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 0,
        call_inline = 1,
        label       = 'n')

    xform3.input_program()
    xform3.output_program()
    
    print "Inlining Test4"
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [2, 1]
    # Input alphabet and order
    in_alp  = [['e', 'r1l', 'r1r', 't1'], ['e', 'r2', 's1']]
    in_ord  = [['e', 'r1l', 'r1r', 't1'], ['e', 's1', 'r2']]

    xform4 = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 0,
        call_inline = 1,
        label       = 'l')

    xform4.input_program()
    xform4.output_program()
    
    print "Inlining Test5"
    # Dimensions
    in_dim  = 3
    out_dim = 3
    # Type of dimensions
    in_dim_type  = [1, 2, 1]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 't2'], ['e', 'r3', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 't2'], ['e', 's1', 'r3']]

    xform5 = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 1,
        call_inline = 1,
        label       = 'l')

    xform5.input_program()
    xform5.output_program()

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

    xform1 = Transformation(
        name        = 'sm',
        in_dim      = in_dim, 
        out_dim     = out_dim, 
        in_dim_type = in_dim_type, 
        in_alp      = in_alp, 
        in_ord      = in_ord, 
        dim_strip   = strip_dim, 
        strip_size  = strip_size)

    xform1.input_program()
    xform1.output_program()
 
    
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
    
    xform2 = Transformation(
        name        = 'sm',
        in_dim      = in_dim, 
        out_dim     = out_dim, 
        in_dim_type = in_dim_type, 
        in_alp      = in_alp, 
        in_ord      = in_ord, 
        dim_strip   = strip_dim, 
        strip_size  = strip_size)

    xform2.input_program()
    xform2.output_program()

def composition_test():
    print "Composition Test"
    # Dimensions
    dim  = 2
    # Type of dimensions
    dim_type = [1, 2]

    # code-motion 
    alp1  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    ord1  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]
    ord2  = [['e', 't1', 'r1'], ['e', 's1', 'r2l', 'r2r']]

    xform1 = Transformation(
        name         = 'cm',
        in_dim       = dim,
        out_dim      = dim,
        in_dim_type  = dim_type,
        in_alp       = alp1,
        in_ord       = ord1,
        out_ord      = ord2)

    # Strip Mining
    strip_dim  = 0
    strip_size = 2

    xform2 = Transformation(
        name        = 'sm',
        in_dim      = xform1.out_dim,
        out_dim     = xform1.out_dim+1,
        in_dim_type = xform1.out_dim_type,
        in_alp      = xform1.out_alp,
        in_ord      = xform1.out_ord,
        dim_strip   = strip_dim,
        strip_size  = strip_size)

    # Interchange
    dim1_ = 1
    dim2_ = 2
    
    xform3 = Transformation(
        name         ='ic',
        in_dim       = xform2.out_dim,
        out_dim      = xform2.out_dim,
        in_dim_type  = xform2.out_dim_type,
        in_alp       = xform2.out_alp,
        in_ord       = xform2.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)

    # Inline
    dim_il   = 1
    call_il  = 1
    label_il = 'l'
    
    xform4 = Transformation(
        name        = 'il',
        in_dim      = xform3.out_dim,
        out_dim     = xform3.out_dim,
        in_dim_type = xform3.out_dim_type,
        in_alp      = xform3.out_alp,
        in_ord      = xform3.out_ord,
        dim_inline  = dim_il,
        call_inline = call_il,
        label       = label_il)

    xform = xform1.compose(xform2).compose(xform3).compose(xform4)

    xform.input_program()
    print "\nTransformation: ", xform.name
    xform.output_program()

if __name__ == "__main__":
    cm_test()
    ic_test()
    il_test()
    sm_test()
    composition_test()
