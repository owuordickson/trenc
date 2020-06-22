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
from .aco_grad_gr_h5 import GradACOgr_h5
from ..aco_tgrad_gr import T_GradACOgr
from ....common.fuzzy_mf import calculate_time_lag
from ....common.gp import GP, TGP
from ....common.profile_cpu import Profile


class GradACOt_grH5 (GradACOgr_h5):

    def __init__(self, d_set, attr_data, t_diffs):
        self.d_set = d_set
        self.time_diffs = t_diffs
        self.attr_index = self.d_set.attr_cols
        # self.e_factor = 0.1  # evaporation factor
        # fetch previous p_matrix from memory
        grp1 = 'dataset/' + self.d_set.step_name + '/p_matrix'
        grp2 = 'dataset/' + self.d_set.step_name + '/steps_matrix'
        p_matrix = self.d_set.read_h5_dataset(grp1)
        steps_matrix = self.d_set.read_h5_dataset(grp2)
        if np.sum(p_matrix) > 0:
            self.p_matrix = p_matrix
            self.steps_matrix = steps_matrix
        else:
            self.p_matrix = np.ones((self.d_set.column_size, 3), dtype=float)
            self.steps_matrix = np.zeros((self.d_set.column_size, 3), dtype=int)
        self.sup_matrix = np.array([])
        self.tstamp_matrix = [[[] for i in range(3)] for j in range(d_set.column_size)]
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
                grp = 'dataset/' + self.d_set.step_name + '/valid_bins/' + gi.as_string()
                temp = self.d_set.read_h5_dataset(grp)
                if bin_data.size <= 0:
                    bin_data = np.array([temp, temp])
                    gen_pattern.add_gradual_item(gi)
                else:
                    bin_data[1] = temp
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

    def run_ant_colony(self):
        min_supp = self.d_set.thd_supp
        winner_gps = list()  # subsets
        loser_gps = list()  # supersets
        repeated = 0
        while repeated < 1:
            rand_gp = self.generate_random_gp()
            if len(rand_gp.gradual_items) > 1:
                # print(rand_gp.get_pattern())
                exits = GradACOgr_h5.is_duplicate(rand_gp, winner_gps, loser_gps)
                if not exits:
                    repeated = 0
                    # check for anti-monotony
                    is_super = GradACOgr_h5.check_anti_monotony(loser_gps, rand_gp, subset=False)
                    is_sub = GradACOgr_h5.check_anti_monotony(winner_gps, rand_gp, subset=True)
                    if is_super or is_sub:
                        continue
                    gen_gp = self.validate_gp(rand_gp)
                    if gen_gp.support >= min_supp:
                        self.deposit_pheromone(gen_gp)
                        is_present = GradACOgr_h5.is_duplicate(gen_gp, winner_gps, loser_gps)
                        is_sub = GradACOgr_h5.check_anti_monotony(winner_gps, gen_gp, subset=True)
                        if is_present or is_sub:
                            repeated += 1
                        else:
                            winner_gps.append(gen_gp)
                    else:
                        loser_gps.append(gen_gp)
                        # update pheromone as irrelevant with loss_sols
                        # self.vaporize_pheromone(gen_gp, self.e_factor)
                    if set(gen_gp.get_pattern()) != set(rand_gp.get_pattern()):
                        loser_gps.append(rand_gp)
                else:
                    repeated += 1
        grp = 'dataset/' + self.d_set.step_name + '/p_matrix'
        self.d_set.add_h5_dataset(grp, self.p_matrix)
        grp = 'dataset/' + self.d_set.step_name + '/steps_matrix'
        self.d_set.add_h5_dataset(grp, self.steps_matrix)
        return winner_gps


class T_GradACOgrH5(T_GradACOgr):

    def __init__(self, d_set, ref_item, min_rep, cores):
        # For tgraank
        self.d_set = d_set
        self.d_set.init_h5_groups()
        cols = self.d_set.time_cols
        if len(cols) > 0:
            print("Dataset Ok")
            self.time_ok = True
            self.time_cols = cols
            self.min_sup = d_set.thd_supp
            self.ref_item = ref_item
            self.d_set.data = self.d_set.read_h5_dataset('dataset/data')
            self.d_set.data = np.array(self.d_set.data).astype('U')
            self.max_step = self.get_max_step(min_rep)
            self.orig_attr_data = self.d_set.data.copy().T
            if cores > 1:
                self.cores = cores
            else:
                self.cores = Profile.get_num_cores()
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
        ac = GradACOt_grH5(d_set, attr_data, time_diffs)
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

