# -*- coding: utf-8 -*-
"""
@author: "Dickson OWUOR"
@credits: "Anne LAURENT, Joseph ORERO"
@version: "1.0"
@email: "owuordickson@gmail.com"
@created: "17 March 2020"

TRENC: Temporal gRadual Emerging aNt Colony optimization
This algorithm implements and modifies

"""

import multiprocessing as mp
import numpy as np
from ...common.profile_cpu import Profile
from ...common.dataset import Dataset
from .aco_grad_gr import GradACOgr
from ...common.gp import GI, GP
from ...common.ep import GEP


class Trenc:

    def __init__(self, f_paths, min_sup, cores=0, allow_para=1):
        self.min_sup = min_sup
        if cores > 1:
            self.cores = cores
        else:
            self.cores = Profile.get_num_cores()
        if allow_para == 0:
            self.allow_parallel = False
            self.msg_para = "False"
        else:
            self.allow_parallel = True
            self.msg_para = "True"

        self.titles = []
        self.d_sets = self.get_csv_data(f_paths)
        if len(self.d_sets) <= 1:
            # Not possible to mine EPs
            raise Exception("Mining EPs requires at least 2 data sets")

    def get_csv_data(self, raw_paths):
        try:
            lst_path = [x.strip() for x in raw_paths.split(',')]
            for path in lst_path:
                if path == '':
                    lst_path.remove(path)
            if len(lst_path) < 2:
                raise Exception("File Path Error: less than 2 paths found")
        except ValueError as error:
            raise Exception("File Path Error: " + str(error))

        if self.allow_parallel:
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            d_sets = pool.map(self.get_dataset, lst_path)
            return d_sets
        else:
            d_sets = list()
            for path in lst_path:
                d_set = self.get_dataset(path)
                d_sets.append(d_set)
            return d_sets

    def get_dataset(self, path):
        d_set = Dataset(path, self.min_sup, eq=False)
        return d_set

    def run_trenc(self, set_id=0):
        # test titles
        ok = self.check_ds_titles()
        if not ok:
            raise Exception("Data sets have different columns")
        else:
            gp_list = self.fetch_patterns()
            geps = Trenc.construct_eps(set_id, gp_list)
            return geps

    def check_ds_titles(self):
        count = len(self.d_sets[0].title)
        for i in range(1, len(self.d_sets)):
            temp = len(self.d_sets[i].title)
            if temp != count:
                return False
        self.titles = self.d_sets[0].title
        return True

    def fetch_patterns(self):
        if self.allow_parallel:
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            # run aco-grad (multiple files)
            aco_objs = pool.map(self.extract_gps, self.d_sets)
        else:
            aco_objs = list()
            for d_set in self.d_sets:
                # run aco-grad (multiple files)
                obj = self.extract_gps(d_set)
                aco_objs.append(obj)
        return aco_objs

    @staticmethod
    def extract_gps(d_set):
        ac = GradACOgr(d_set)
        ac.run_ant_colony()
        p_matrix = (ac.p_matrix - 1)
        st_matrix = ac.steps_matrix

        with np.errstate(divide='ignore', invalid='ignore'):
            temp = np.true_divide(p_matrix, st_matrix)
            temp[temp == np.inf] = 0  # convert inf to 0
            temp = np.nan_to_num(temp)  # convert Nan to 0

        ac.sup_matrix = temp
        # for p in pats:
        #    print(str(p.to_string()) + str(p.support))
        return ac

    @staticmethod
    def construct_eps(ds_id, gp_list):
        geps = list()
        if ds_id < len(gp_list):
            # 1. generate GR matrix
            gp_1 = gp_list[ds_id]
            GR_matrix = gp_1.sup_matrix
            for gp_2 in gp_list:
                matrix = gp_2.sup_matrix
                if np.array_equal(GR_matrix, matrix):
                    continue
                else:
                    with np.errstate(divide='ignore', invalid='ignore'):
                        temp = np.true_divide(GR_matrix, matrix)
                        # inf means that the pattern is missing in 1 or more
                        # data-sets (JEP), so we remove it by converting it to 0
                        temp[temp == np.inf] = -1  # convert inf to -1
                        temp = np.nan_to_num(temp)  # convert Nan to 0
                    # GR = [temp, gp_1, gp_2]
                    # GR_list.append(GR)
                    # 2. construct EPs
                    temp_geps = Trenc.construct_gps(temp)
                    for ep in temp_geps:
                        geps.append(ep)
                    #for jep in temp_jeps:
                    #    jeps.append(jep)
            return geps
        else:
            raise Exception("Selected data-set/file does not exist")

    @staticmethod
    def construct_gps(GR_matrix):
        eps = list()
        jeps = list()
        geps = list()
        size = len(GR_matrix)

        # 1. normalize GR_matrix (pick largest GR for every attribute)
        for i in range(size):
            row = GR_matrix[i]
            if (row[0] >= row[1]) and (row[1] != -1):
                GR_matrix[i][1] = 0
            elif (row[1] >= row[0]) and (row[0] != -1):
                GR_matrix[i][0] = 0

        # 2. construct eps
        for i in range(size):
            attr = i
            row_i = GR_matrix[i]
            incr = row_i[0]
            decr = row_i[1]

            if incr > 0 or incr == -1:
                gp = GP()
                gp.add_gradual_item(GI(attr, '+'))
                pat = [gp, incr]
                for j in range(i+1, size, 1):
                    row_j = GR_matrix[j]
                    pat = Trenc.combine_patterns(pat, row_j, j)
                if len(pat[0].gradual_items) > 1:
                    if pat[1] == -1:
                        gep = GEP(pat[0])
                    #    jeps.append(jep)
                    else:
                        gep = GEP(pat[0], pat[1])
                    #    eps.append(ep)
                    geps.append(gep)

            if decr > 0 or decr == -1:
                gp = GP()
                gp.add_gradual_item(GI(attr, '-'))
                pat = [gp, decr]
                for j in range(i+1, size, 1):
                    row_j = GR_matrix[j]
                    pat = Trenc.combine_patterns(pat, row_j, j)
                if len(pat[0].gradual_items) > 1:
                    if pat[1] == -1:
                        jep = GEP(pat[0])
                        #jeps.append(jep)
                    else:
                        ep = GEP(pat[0], pat[1])
                        #eps.append(ep)
                    geps.append(gep)
        # print([ep, jep])
        return geps

    @staticmethod
    def combine_patterns(pat, row, attr):
        if row[0] > 0:
            dir_ = row[0]
            sign = '+'
        elif row[1] > 0:
            dir_ = row[1]
            sign = '-'
        else:
            return []

        if dir_ > 0 or dir_ == -1:
            temp = GI(attr, sign)
            pat[0].add_gradual_item(temp)
            if dir_ < pat[1]:
                pat[1] = dir_
            return pat
        else:
            return []