# -*- coding: utf-8 -*-
"""
@author: "Dickson Owuor"
@credits: "Anne Laurent and Joseph Orero"
@license: "MIT"
@version: "2.0"
@email: "owuordickson@gmail.com"
@created: "19 November 2019"



Description: updated version that uses aco-graank and parallel multi-processing

"""

from ...common.graank_v2 import graank
from ...common.t_graank import Tgrad
from .border_tgraank import check_for_pattern, get_maximal_items


class T_Grad_gr(Tgrad):

    def __init__(self, f_path, eq, ref_item, min_sup, min_rep, cores):
        super().__init__(f_path, eq, ref_item, min_sup, min_rep, cores)

    def fetch_patterns(self, step):
        step += 1  # because for-loop is not inclusive from range: 0 - max_step
        # 1. Transform data
        d_set = self.d_set
        attr_data, time_diffs = self.transform_data(step)

        # 2. Execute t-graank for each transformation
        d_set.update_attributes(attr_data)
        tgps = graank(t_diffs=time_diffs, d_set=d_set)

        if len(tgps) > 0:
            gp_list = list()
            tlag_list = list()
            for tgp in tgps:
                gp_list.append(tgp.get_tuples())
                tlag_list.append(tgp.time_lag)
            #return tgps
            pattern_found = check_for_pattern(self.ref_item, gp_list)
            if pattern_found:
                maximal_items = get_maximal_items(gp_list, tlag_list)
                # tgps.append(tuple((title, maximal_items)))
                return tuple((d_set.title, maximal_items))
        return False
