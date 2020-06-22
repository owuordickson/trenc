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
import multiprocessing as mp
from .aco_grad_gr import GradACOgr
from ...common.fuzzy_mf import calculate_time_lag
from ...common.gp import GP, TGP
from ...common.dataset import Dataset
from ...common.profile_cpu import Profile


class GradACOt_gr (GradACOgr):

    def __init__(self, d_set, attr_data, t_diffs):
        super().__init__(d_set)
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
                self.p_matrix[i][0] += pattern.support
                self.steps_matrix[i][0] += 1
                self.tstamp_matrix[i][0].append([pattern.time_lag.timestamp, pattern.time_lag.support])
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
                        bin_data[1] = bin_data[1]
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


class T_GradACOgr:

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

    def get_max_step(self, min_rep):  # optimized
        all_rows = len(self.d_set.data)
        return all_rows - int(min_rep * all_rows)

    def run_tgraank(self, parallel=False):
        if not parallel:
            # implement parallel multi-processing
            if self.cores > 1:
                num_cores = self.cores
            else:
                num_cores = Profile.get_num_cores()
                self.cores = num_cores

            self.cores = num_cores
            steps = range(self.max_step)
            # pool = mp.Pool(num_cores)
            with mp.Pool(num_cores) as pool:
                aco_objs = pool.map(self.fetch_patterns, steps)
                # pool.close()
                # pool.join()
            return aco_objs
        else:
            aco_objs = list()
            for step in range(self.max_step):
                ac = self.fetch_patterns(step)
                if ac:
                    aco_objs.append(ac)
            return aco_objs

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

    def transform_data(self, step):  # optimized
        # NB: Restructure dataset based on reference item
        if self.time_ok:
            # 1. Calculate time difference using step
            ok, time_diffs = self.get_time_diffs(step)
            if not ok:
                msg = "Error: Time in row " + str(time_diffs[0]) \
                      + " or row " + str(time_diffs[1]) + " is not valid."
                raise Exception(msg)
            else:
                ref_col = self.ref_item
                if ref_col in self.time_cols:
                    msg = "Reference column is a 'date-time' attribute"
                    raise Exception(msg)
                elif (ref_col < 0) or (ref_col >= len(self.d_set.title)):
                    msg = "Reference column does not exist\nselect column between: " \
                          "0 and " + str(len(self.d_set.title) - 1)
                    raise Exception(msg)
                else:
                    # 1. Split the transpose data set into column-tuples
                    attr_data = self.orig_attr_data

                    # 2. Transform the data using (row) n+step
                    new_attr_data = list()
                    size = len(attr_data)
                    for k in range(size):
                        col_index = k
                        tuples = attr_data[k]
                        n = tuples.size
                        # temp_tuples = np.empty(n, )
                        # temp_tuples[:] = np.NaN
                        if col_index in self.time_cols:
                            # date-time attribute
                            temp_tuples = tuples[:]
                        elif col_index == ref_col:
                            # reference attribute
                            temp_tuples = tuples[0: n - step]
                        else:
                            # other attributes
                            temp_tuples = tuples[step: n]
                        # print(temp_tuples)
                        new_attr_data.append(temp_tuples)
                    return new_attr_data, time_diffs
        else:
            msg = "Fatal Error: Time format in column could not be processed"
            raise Exception(msg)

    def get_time_diffs(self, step):  # optimized
        data = self.d_set.data
        size = len(data)
        time_diffs = []
        for i in range(size):
            if i < (size - step):
                # for col in self.time_cols:
                col = self.time_cols[0]  # use only the first date-time value
                temp_1 = str(data[i][int(col)])
                temp_2 = str(data[i + step][int(col)])
                stamp_1 = Dataset.get_timestamp(temp_1)
                stamp_2 = Dataset.get_timestamp(temp_2)
                if (not stamp_1) or (not stamp_2):
                    return False, [i + 1, i + step + 1]
                time_diff = (stamp_2 - stamp_1)
                # index = tuple([i, i + step])
                # time_diffs.append([time_diff, index])
                time_diffs.append([time_diff, i])
        return True, np.array(time_diffs)
