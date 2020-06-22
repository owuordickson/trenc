# -*- coding: utf-8 -*-

"""
Created on Fri Jun 12 14:31:16 2015

@author: Olivier + modif MJL+MR 140316

Modified on Tue Oct 23 2018 by Dickson Owuor

Description: This code (originally) correlates gradual patterns using concordant pairs
                We added a functionality that allows for retrieval of time lags from concordant
                indices, approximation using a fuzzy membership function
                T-GRAANK - denotes Temporal GRAANK (GRAdual rANKing) and User interface
Usage:
    $python t_graank.py -f DATASET.csv -c refColumn -s minSupport  -r minRepresentativity
    $python t_graank.py -f test.csv -c 0 -s 0.5 -r 0.5

"""


from src.border_ep.algorithms.border_diff import gen_set


def check_for_pattern(ref_item, R):
    ref_gi_pos = tuple([ref_item, '+'])
    ref_gi_neg = tuple([ref_item, '-'])
    pr = 0
    for i in range(len(R)):
        # D is the Gradual Patterns, S is the support for D and T is time lag
        if (ref_gi_pos in R[i]) or (ref_gi_neg in R[i]):
            # select only relevant patterns w.r.t *reference item
            pr = pr + 1
    if pr > 0:
        return True
    else:
        return False


def get_maximal_items(init_list, tlag_list):
    comb = list((zip(init_list, tlag_list)))
    max_items = gen_set(tuple(init_list))

    for item_i in max_items:
        for item_j in max_items:
            if set(item_i).issubset(set(item_j)) and set(item_i) != (set(item_j)):
                try:
                    # temp.remove(item_i)
                    for item in comb:
                        if tuple(item[0]) == item_i:
                            comb.remove(item)
                except Exception:
                    continue
    return comb

