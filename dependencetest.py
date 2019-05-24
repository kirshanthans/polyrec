#!/usr/bin/python
import sys, os
from statemachines import MultiTapeFSA, MultiTapeFST
from transformations import Transformation

class Dependence:
    def __init__(prefix, suffix1, suffix2):
        self.prefix  = prefix
        self.suffix1 = suffix1
        self.suffix2 = suffix2

    def test(self, xform):
        return is_safe(self.suffix1, self.suffix2, xform.fst)

    @staticmethod
    def is_safe(witness_fsa1, witness_fsa2, fst_xform):
        """
        checking witness tuples on a given xform 
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
    
    @staticmethod
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

    @staticmethod
    def path_test(late_path, early_path, dict_alph):
        dims = len(dict_alph)
        for i in xrange(dims):
            res = dep_test(late_path[i], early_path[i], dict_alph[i])
            if res is None:
                continue
            else:
                return res

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
        return list_re

