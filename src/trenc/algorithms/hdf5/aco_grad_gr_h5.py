# -*- coding: utf-8 -*-
"""
@author: "Dickson Owuor"
@credits: "Anne Laurent"
@license: "MIT"
@version: "2.0"
@email: "owuordickson@gmail.com"
@created: "12 July 2019"
@modified: "16 June 2020"

"""

import numpy as np
from ....common.hdf5.aco_grad_h5 import GradACO_h5
from ....common.gp import GP


class GradACOgr_h5(GradACO_h5):

    def __init__(self, d_set):
        self.d_set = d_set
        self.d_set.init_attributes()
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

    def deposit_pheromone(self, pattern=GP()):
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
            elif symbol == '-':
                self.p_matrix[i][1] += pattern.support
                self.steps_matrix[i][1] += 1
        for index in self.attr_index:
            if int(index) not in lst_attr:
                i = int(index)
                self.p_matrix[i][2] += 1

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
