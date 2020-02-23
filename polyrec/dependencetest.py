import sys, os
from polyrec.statemachines import MultiTapeFSA, MultiTapeFST
from polyrec.transformations import Transformation
from polyrec.witnesstuples import WitnessTuple

class Path:
    def __init__(self, fsa):
        self.fsa         = fsa   # state machine
        self.path        = None  # path as a dictionary key: dimension, value: [labels]
        self.mul_path    = None  # path as a list of tuples (label, dimension)
        self.cycle_path  = None  # part of mul_path that recurs
        self.state_chain = None  # chain of states
        self.recur       = None  # True if the path does not end in a final state
        self.cycle_path  = None  # cyclic part of the path (beta in alpha(beta)*)
        self.dictionary  = None  # a list of dictionaries for each dimension key: label value: rank
        self.flat_dict   = None  # a dictionary key: label value: rank (in a total program order)
        self.pg_ord      = None  # a list of labels including empty string in total program order

    def gdict(self):
        #construct an alphabetically ordered dictionary per dimension
        dims = self.fsa.dims
        odrs = self.fsa.order
        
        self.dictionary = []
        self.flat_dict  = {}
        self.pg_ord     = ['e']
       
        for i in range(dims):
            self.pg_ord += odrs[i][1:] # creating the flat statement order
            rank = {}
            odr_dim = odrs[i]
            for j in range(len(odr_dim)):
                rank[odr_dim[j]] = j-1
            self.dictionary.append(rank)
        
        for i in range(len(self.pg_ord)):
            self.flat_dict[self.pg_ord[i]] = i-1
    
    def find_edge_latest(self, curr_state):
        #finding the latest edge from a given state
        next_state = None
        alph       = 'e'
        dim        = -1
        rank       = -1
    
        outgoing = self.fsa.edges[curr_state]
        for i in range(self.fsa.dims):
            dict_dim = self.dictionary[i]
            for end, tup in outgoing:
                rank_ = dict_dim[tup[i]]
                alph_ = tup[i]
                if rank_ >= 0 and rank_ > rank:
                    rank       = rank_
                    alph       = alph_
                    dim        = i
                    next_state = end
            if alph is not 'e':
                break

        return alph, dim, next_state

    def latest_path(self, init_state):
        # designed to handle given initial state
        # list of dict gives the alphabetical order by dimension
        dims = self.fsa.dims

        self.path = {} # index i holds the part of path from dimension i
        self.mul_path = [] # path as list of tuples
        for i in range(dims):
            self.path[i] = []
        self.state_chain = [] # state chain from the initial stage

        curr_state = init_state # initializing current stage

        while curr_state not in self.state_chain and curr_state not in self.fsa.final_states:
            
            if curr_state not in self.fsa.edges:
                return False
            # escaping the null transitions
            if len(self.fsa.edges[curr_state]) == 1 and self.fsa.edges[curr_state][0][1] == tuple(['e']*dims):
                self.state_chain.append(curr_state)
                curr_state = self.fsa.edges[curr_state][0][0]

            alph, dim, next_state = self.find_edge_latest(curr_state) # finding the latest edge

            self.path[dim].append(alph) # add label to the correct dimension

            self.mul_path.append((alph, dim)) # constructing the tuple for multi path

            self.state_chain.append(curr_state) # appending the state chain

            curr_state = next_state # setting current state to the next

        if curr_state not in self.fsa.final_states: # finding whether it is a recurring path
            self.recur = True
        else:
            self.recur = False

        for i in range(len(self.state_chain)): # finding the cycle
            if self.state_chain[i] == curr_state:
                self.cycle_path = self.mul_path[i:]
                break
        
        return True

    def find_edge_earliest(self, curr_state):
        # finding the earliest edge from a given state
        next_state = None
        alph       = 'e'
        dim        = -1
        rank       = sys.maxsize
    
        outgoing = self.fsa.edges[curr_state]
        for i in range(self.fsa.dims):
            dict_dim = self.dictionary[i]
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
    
    def earliest_path(self, init_state):
        # designed to handle given initial state
        # list of dict gives the alphabetical order by dimension
        dims = self.fsa.dims

        self.path = {} # index i holds the part of path from dimension i
        self.mul_path = [] # path as list of tuples
        for i in range(dims):
            self.path[i] = []
        self.state_chain = [] # state chain from the initial stage

        curr_state = init_state # initializing current state

        while curr_state not in self.state_chain and curr_state not in self.fsa.final_states:
            if curr_state not in self.fsa.edges:
                return False
            # escaping the null transitions
            if len(self.fsa.edges[curr_state]) == 1 and self.fsa.edges[curr_state][0][1] == tuple(['e']*dims):
                self.state_chain.append(curr_state)
                curr_state = self.fsa.edges[curr_state][0][0]

            alph, dim, next_state = self.find_edge_earliest(curr_state) # finding the earliest edge

            self.path[dim].append(alph) # add label to the correct dimension
            
            self.mul_path.append((alph, dim)) # constructing the tuple for multi path

            self.state_chain.append(curr_state) # appending the state chain

            curr_state = next_state # setting current state to the next

        if curr_state not in self.fsa.final_states: # finding whether it is a recurring path
            self.recur = True
        else:
            self.recur = False

        for i in range(len(self.state_chain)): # finding the cycle
            if self.state_chain[i] == curr_state:
                self.cycle_path = self.mul_path[i:]
                break
        
        return True

    def extend_path(self, times):
        assert self.recur == True

        for _ in range(times):
            self.mul_path += self.cycle_path
            for l,d in self.cycle_path:
                self.path[d].append(l)

class Dependence:
    def __init__(self, witness):
        self.prefix  = None 
        self.suffix1 = witness.fsa1
        self.suffix2 = witness.fsa2

    def test(self, xform):
        # dependence fst will have only one initial state
        dep_fst1 = self.suffix1.identity_fst() # constructing the dependence fst for suffix 1
        dep_fst2 = self.suffix2.identity_fst() # constructing the dependence fst for suffix 2

        dep_fsa1 = dep_fst1.compose_fst(xform.fst).project_out()
        dep_fsa2 = dep_fst2.compose_fst(xform.fst).project_out()

        path1 = Path(dep_fsa1)
        path2 = Path(dep_fsa2)

        path1.gdict() # computing dictionaries
        path2.gdict() # computing dictionaries
        
        assert path1.dictionary == path2.dictionary
        assert path1.flat_dict  == path2.flat_dict
        assert path1.pg_ord     == path2.pg_ord
        
        for s1 in path1.fsa.init_states:
            for s2 in path2.fsa.init_states:
                
                status1 = path1.latest_path(s1)
                status2 = path2.earliest_path(s2)

                if not status1 or not status2:
                    continue

                t_val = Dependence.dim_test(path1.path, path2.path, path1.dictionary)
                if t_val == False:
                    return False

        return True
    
    @staticmethod
    def dim_test(late_path, early_path, dict_alph):
        dims = len(dict_alph)
        for i in range(dims):
            res = Dependence.ord_test(late_path[i], early_path[i], dict_alph[i])
            if res is None:
                continue
            else:
                return res
        return False

    @staticmethod
    def ord_test(late_path, early_path, dict_alph):
        if len(late_path) is 0 and len(early_path) is 0:
            return None
        elif len(late_path) is 0 and len(early_path) is not 0:
            return True
        elif len(late_path) is not 0 and len(early_path) is 0:
            return False
        elif dict_alph[late_path[0]] < dict_alph[early_path[0]]:
            return True 
        elif dict_alph[late_path[0]] > dict_alph[early_path[0]]:
            return False 
        return Dependence.ord_test(late_path[1:], early_path[1:], dict_alph)

def deptest_cm():   
    print("Code Motion Test")
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

    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))
 
def deptest_ic():
    print("Interchange Test")
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    xform = Transformation(
        name         ='ic',
        in_dim       = in_dim,
        out_dim      = out_dim,
        in_dim_type  = in_dim_type,
        in_alp       = in_alp,
        in_ord       = in_ord,
        dim_i1       = 0,
        dim_i2       = 1)
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))

def deptest_il():
    print("Inlining Test")
    # Dimensions
    in_dim  = 2
    out_dim = 2
    # Type of dimensions
    in_dim_type  = [1, 2]
    # Input alphabet and order
    in_alp  = [['e', 'r1', 't1'], ['e', 'r2l', 'r2r', 's1']]
    in_ord  = [['e', 't1', 'r1'], ['e', 'r2l', 'r2r', 's1']]

    xform = Transformation(
        name        = 'il',
        in_dim      = in_dim,
        out_dim     = out_dim,
        in_dim_type = in_dim_type,
        in_alp      = in_alp,
        in_ord      = in_ord,
        dim_inline  = 1,
        call_inline = 1,
        label       = 'l')

    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    
    wtuple = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple.set_fsa()

    Dep = Dependence(wtuple)

    print(Dep.test(xform))

def deptest_sm():
    print("Strip-Mining Test")
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

    xform = Transformation(
        name        = 'sm',
        in_dim      = in_dim, 
        out_dim     = out_dim, 
        in_dim_type = in_dim_type, 
        in_alp      = in_alp, 
        in_ord      = in_ord, 
        dim_strip   = strip_dim, 
        strip_size  = strip_size)

    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    
    wtuple = WitnessTuple(in_dim, in_dim_type, in_alp, in_ord, rgx1, rgx2)
    wtuple.set_fsa()

    Dep = Dependence(wtuple)

    print(Dep.test(xform))

def deptest_cm_sm_ic_il():
    print("CM-SM-IC-IL Test")
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
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', '(r1)*', 't1'], ['s1']]
    
    wtuple = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple.set_fsa()

    Dep = Dependence(wtuple)

    print(Dep.test(xform))

def deptest_cm_ic():
    print("CM-IC Test")
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
    
    # interchange
    dim1_ = 0
    dim2_ = 1
    
    xform2 = Transformation(
        name         ='ic',
        in_dim       = xform1.out_dim,
        out_dim      = xform1.out_dim,
        in_dim_type  = xform1.out_dim_type,
        in_alp       = xform1.out_alp,
        in_ord       = xform1.out_ord,
        dim_i1       = dim1_,
        dim_i2       = dim2_)
    
    xform = xform1.compose(xform2)
    
    # regex for witness tuple    
    rgx1 = [['t1'], ['s1']]
    rgx2 = [['r1', 't1'], ['(r2l|r2r)', 's1']]
    
    wtuple1 = WitnessTuple(dim, dim_type, alp1, ord1, rgx1, rgx2)
    wtuple1.set_fsa()

    Dep1 = Dependence(wtuple1)

    print("Tuple1: ", Dep1.test(xform))
    
    rgx3 = [['t1'], ['(r2l|r2r)', 's1']]
    rgx4 = [['t1'], ['s1']]
    
    wtuple2 = WitnessTuple(dim, dim_type, alp1, ord1, rgx3, rgx4)
    wtuple2.set_fsa()

    Dep2 = Dependence(wtuple2)

    print("Tuple2: ", Dep2.test(xform))

if __name__ == "__main__":
    deptest_cm()
    deptest_ic()
    #deptest_il()
    #deptest_sm()
    #deptest_cm_sm_ic_il()
    deptest_cm_ic()
