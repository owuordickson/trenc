# -*- coding: utf-8 -*-
"""
@author: "Dickson Owuor"
@credits: "Thomas Runkler and Anne Laurent,"
@license: "MIT"
@version: "2.4"
@email: "owuordickson@gmail.com"
@created: "19 November 2019"
@modified: "11 June 2020"

Description: updated version that uses aco-graank and parallel multi-processing

"""


import numpy as np
from .aco_grad_gr import GradACOgr
from .common.aco_tgrad import T_GradACO
from .common.fuzzy_mf import calculate_time_lag
from .common.gp import GP, TGP


class GradACOt_gr (GradACOgr):

    def __init__(self, d_set, attr_data, t_diffs):
        self.d_set = d_set
        self.attr_index = self.d_set.attr_cols
        # self.e_factor = 0.1  # evaporation factor
        self.p_matrix = np.ones((self.d_set.column_size, 3), dtype=float)
        self.steps_matrix = np.zeros((self.d_set.column_size, 3), dtype=int)
        self.sup_matrix = np.array([])
        self.tstamp_matrix = [[[] for i in range(3)] for j in range(d_set.column_size)]
        self.time_diffs = t_diffs
        self.d_set.update_attributes(attr_data)

    def deposit_pheromone(self, pattern=TGP()):
        lst_attr = []
        for obj in pattern.gradual_items:
            # print(obj.attribute_col)
            attr = obj.attribute_col
            symbol = obj.symbol
            lst_attr.append(attr)
            i = attr
            if symbol == '+':
                self.p_matrix[i][0] += pattern.support
                self.steps_matrix[i][0] += 1
                self.tstamp_matrix[i][0].append([pattern.time_lag.timestamp, pattern.time_lag.support])
            elif symbol == '-':
                self.p_matrix[i][1] += pattern.support
                self.steps_matrix[i][1] += 1
                self.tstamp_matrix[i][1].append([pattern.time_lag.timestamp, pattern.time_lag.support])
        for index in self.attr_index:
            if int(index) not in lst_attr:
                i = int(index)
                self.p_matrix[i][2] += 1

    def validate_gp(self, pattern):
        # pattern = [('2', '+'), ('4', '+')]
        min_supp = self.d_set.thd_supp
        gen_pattern = GP()
        bin_data = np.array([])

        for gi in pattern.gradual_items:
            if self.d_set.invalid_bins.size > 0 and np.any(np.isin(self.d_set.invalid_bins, gi.gradual_item)):
                continue
            else:
                arg = np.argwhere(np.isin(self.d_set.valid_bins[:, 0], gi.gradual_item))
                if len(arg) > 0:
                    i = arg[0][0]
                    bin_obj = self.d_set.valid_bins[i]
                    if bin_data.size <= 0:
                        bin_data = np.array([bin_obj[1], bin_obj[1]])
                        gen_pattern.add_gradual_item(gi)
                    else:
                        bin_data[1] = bin_obj[1]
                        temp_bin, supp = self.bin_and(bin_data, self.d_set.attr_size)
                        if supp >= min_supp:
                            bin_data[0] = temp_bin
                            gen_pattern.add_gradual_item(gi)
                            gen_pattern.set_support(supp)
        if len(gen_pattern.gradual_items) <= 1:
            tgp = TGP(gp=pattern)
            return tgp
        else:
            # t_lag = FuzzyMF.calculate_time_lag(FuzzyMF.get_patten_indices(bin_data[0]), t_diffs, min_supp)
            t_lag = calculate_time_lag(bin_data[0], self.time_diffs)
            if t_lag.support <= 0:
                gen_pattern.set_support(0)
            tgp = TGP(gp=gen_pattern, t_lag=t_lag)
            return tgp


class T_GradACOgr(T_GradACO):

    def __init__(self, d_set, ref_item, min_rep, cores):
        # For tgraank
        self.d_set = d_set
        cols = self.d_set.time_cols
        if len(cols) > 0:
            print("Dataset Ok")
            self.time_ok = True
            self.time_cols = cols
            self.min_sup = d_set.thd_supp
            self.ref_item = ref_item
            self.max_step = self.get_max_step(min_rep)
            self.orig_attr_data = self.d_set.data.copy().T
            self.cores = cores
        else:
            print("Dataset Error")
            self.time_ok = False
            self.time_cols = []
            raise Exception('No date-time data found')

    def fetch_patterns(self, step):
        step += 1  # because for-loop is not inclusive from range: 0 - max_step
        # 1. Transform data
        d_set = self.d_set
        attr_data, time_diffs = self.transform_data(step)

        # 2. Execute aco-graank for each transformation
        ac = GradACOt_gr(d_set, attr_data, time_diffs)
        list_gp = ac.run_ant_colony()

        # 3. Update Support Matrix
        p_matrix = (ac.p_matrix - 1)
        st_matrix = ac.steps_matrix

        with np.errstate(divide='ignore', invalid='ignore'):
            temp = np.true_divide(p_matrix, st_matrix)
            temp[temp == np.inf] = 0  # convert inf to 0
            temp = np.nan_to_num(temp)  # convert Nan to 0
        ac.sup_matrix = temp
        return ac
        #if len(list_gp) > 0:
        #    return ac
        #return False

