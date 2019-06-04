#!/usr/bin/python
def suffix_fsa0(fsa): #[t1, s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]

    fsa.add_transition(0, 1, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa1(fsa): #[r1+t1, s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa2(fsa): #[r1t1, s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa3(fsa): #[t1, rl2s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[0], alph_dim2[1]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa4(fsa): #[t1, rr2s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[0], alph_dim2[2]))
    fsa.add_transition(1, 2, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(2, 3, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa5(fsa): #[r1t1, rl2s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[1]))
    fsa.add_transition(2, 3, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(3, 4, (alph_dim1[0], alph_dim2[3]))

def suffix_fsa6(fsa): #[r1t1, rr2s1]
    #alp: [['e', 'r1', 't1'], ['e', 'rl2', 'rr2', 's1']]
    alph_dim1  = fsa.alphabet[0]
    alph_dim2  = fsa.alphabet[1]
    
    fsa.add_transition(0, 1, (alph_dim1[1], alph_dim2[0]))
    fsa.add_transition(1, 2, (alph_dim1[0], alph_dim2[2]))
    fsa.add_transition(2, 3, (alph_dim1[2], alph_dim2[0]))
    fsa.add_transition(3, 4, (alph_dim1[0], alph_dim2[3]))

class WitnessTuple:
    def __init__(self, dims, alphabet, regex):
        assert dims == len(alphabet)
        assert dims == len(regex)

        self.dims  = dims
        self.alp   = alphabet
        self.regex = regex