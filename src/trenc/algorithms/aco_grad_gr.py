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
from ...common.aco_grad import GradACO
from ...common.gp import GP


class GradACOgr(GradACO):

    def __init__(self, d_set):
        self.d_set = d_set
        self.d_set.init_attributes()
        self.attr_index = self.d_set.attr_cols
        # self.e_factor = 0.1  # evaporation factor
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
