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
from src.algorithms.trenc.multiprocess import InitParallel
from src.algorithms.trenc.handle_data import HandleData
from src.algorithms.trenc.aco_grad import GradACO
from src.algorithms.trenc.aco_t_graank import TgradACO


class Trenc:

    def __init__(self, f_paths, min_sup, cores=0, allow_para=1, min_rep=None, ref_item=None):
        self.file_paths = Trenc.test_paths(f_paths)
        self.ref_item = ref_item
        self.min_rep = min_rep
        self.min_sup = min_sup
        self.titles = []
        self.GR_list = []

        if allow_para == 0:
            self.allow_parallel = False
        else:
            self.allow_parallel = True
            if cores > 1:
                self.cores = cores
            else:
                self.cores = InitParallel.get_num_cores()
        self.d_sets = self.get_csv_data()
        if (len(self.d_sets) <= 1) and self.min_rep is None:
            raise Exception("min_representativity and/or reference column required")
        elif (len(self.d_sets) <= 1) and (self.min_rep is not None):
            d_set = self.d_sets[0]
            self.tg_set = TgradACO(d_set, self.ref_item,
                                   self.min_sup, self.min_rep, 0)
            self.d_sets = self.get_transform_data()

    def get_csv_data(self):
        if self.allow_parallel:
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            d_sets = pool.map(Trenc.fetch_csv_data, self.file_paths)
            return d_sets
        else:
            d_sets = list()
            for path in self.file_paths:
                d_set = Trenc.fetch_csv_data(path)
                d_sets.append(d_set)
            return d_sets

    def get_transform_data(self):
        if self.allow_parallel:
            steps = range(self.tg_set.max_step)
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            d_sets = pool.map(self.fetch_transform_data, steps)
            return d_sets
        else:
            d_sets = list()
            for step in range(self.tg_set.max_step):
                d_set = self.fetch_transform_data(step)
                d_sets.append(d_set)
            return d_sets

    def run_trenc(self, set_id=0):
        # test titles
        ok = self.compare_ds_titles()
        if not ok:
            raise Exception("Data sets have different columns")
        else:
            gp_list = self.fetch_patterns()
            self.GR_list = Trenc.gen_GR_matrix(set_id, gp_list)
            Trenc.fetch_eps(self.GR_list)
            # return self.GR_list

    def fetch_patterns(self):
        if self.allow_parallel:
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            if self.min_rep is None:
                # run aco-grad (multiple files)
                aco_objs = pool.map(self.extract_gps, self.d_sets)
            else:
                # run aco-tgrad (single file)
                aco_objs = pool.starmap(self.extract_gps, self.d_sets)
        else:
            aco_objs = list()
            for d_set in self.d_sets:
                if self.min_rep is None:
                    # run aco-grad (multiple files)
                    obj = self.extract_gps(d_set)
                else:
                    # run aco-tgrad (single file)
                    obj = self.extract_gps(d_set[0], d_set[1])
                aco_objs.append(obj)
        return aco_objs

    def extract_gps(self, d_set, time_diffs=None):
        if d_set is not False:
            ac = GradACO(d_set)
            ac.run_ant_colony(self.min_sup, time_diffs)
            p_matrix = (ac.p_matrix - 1)
            st_matrix = ac.steps_matrix

            with np.errstate(divide='ignore', invalid='ignore'):
                temp = np.true_divide(p_matrix, st_matrix)
                temp[temp == np.inf] = 0  # convert inf to 0
                temp = np.nan_to_num(temp)  # convert Nan to 0

            ac.sup_matrix = temp
            return ac
        else:
            raise Exception("one of the data sets is not valid")

    def compare_ds_titles(self):
        if self.min_rep is not None:
            self.titles = self.d_sets[0][0].title
            return True
        else:
            for d_set in self.d_sets:
                titles_1 = d_set.title
                for obj_set in self.d_sets:
                    titles_2 = obj_set.title
                    if titles_1 == titles_2:
                        continue
                    else:
                        for title_1 in titles_1:
                            ok = Trenc.test_titles(title_1, titles_2)
                            if not ok:
                                return False
            self.titles = self.d_sets[0].title
            return True

    def fetch_transform_data(self, step):
        tg_set = self.tg_set
        step += 1  # because for-loop is not inclusive from range: 0 - max_step
        # 1. Calculate representativity
        chk_rep, rep_info = tg_set.get_representativity(step)
        if chk_rep:
            # 2. Transform data
            tg_set.d_set.attr_data = tg_set.orig_attr_data
            data, time_diffs = tg_set.transform_data(step)
            tg_set.d_set.attr_data = data
            tg_set.d_set.lst_bin = []
            return [tg_set.d_set, time_diffs]
        else:
            raise Exception("Problem with representativity: " + str(rep_info))

    @staticmethod
    def fetch_eps(GR_list):
        ep_list = list()
        for GR in GR_list:
            eps, jeps = Trenc.construct_eps(GR[0])
            print([eps, jeps])
        return ep_list

    @staticmethod
    def construct_eps(GR_matrix):
        eps = list()
        jeps = list()
        size = len(GR_matrix)
        ep = list()
        jep = list()
        for i in range(size):
            attr = i
            row_i = GR_matrix[i]
            incr = row_i[0]
            decr = row_i[1]
            if incr == -1:
                temp = tuple([attr, '+'])
                jep.append(temp)
            elif incr > 1:
                temp = [tuple([attr, '+']), incr]
                ep.append(temp)
            if decr == -1:
                temp = tuple([attr, '-'])
                jep.append(temp)
            elif decr > 1:
                temp = [tuple([attr, '-']), decr]
                ep.append(temp)

    @staticmethod
    def construct_eps1(GR_matrix):
        eps = list()
        jeps = list()  # coded as -1 in GR_matrix

        ep, jep = Trenc.init_gen_ep(GR_matrix, '+')
        eps.append(ep) if ep else eps
        jeps.append(jep) if jep else jeps

        ep, jep = Trenc.init_gen_ep(GR_matrix, '-')
        eps.append(ep) if ep else eps
        jeps.append(jep) if jep else jeps

        return eps, jeps

    @staticmethod
    def init_gen_ep(GR_matrix, sign):
        size = len(GR_matrix)
        ep = list()
        jep = list()
        # gr = 0
        for i in range(size):
            attr = i
            row_i = GR_matrix[i]
            if sign == '+':
                dir_ = row_i[0]
            elif sign == '-':
                dir_ = row_i[1]
            else:
                return False, False
            if dir_ == -1 and not jep:
                pat = tuple([attr, sign])
                jep.append(pat)
                # continue
            elif dir_ > 0 and not ep:
                pat_pos = [[tuple([attr, sign])], dir_]
                pat_neg = [[tuple([attr, sign])], dir_]
                for j in range(i+1, size, 1):
                    row_j = GR_matrix[j]
                    pat = Trenc.get_n_set(pat_pos, pat_neg)
                    pat_pos = Trenc.combine_patterns_test1(pat_pos, row_j, j, '+')
                    pat_neg = Trenc.combine_patterns_test1(pat_neg, row_j, j, '-')
                ep.append(pat_pos)
                ep.append(pat_neg)
                # continue
        ep = False if not ep else ep
        jep = False if not jep else jep
        return ep, jep

    @staticmethod
    def get_n_set(pat_pos, pat_neg):
        pat = list()

        return pat

    @staticmethod
    def combine_patterns_test2(pat, row, attr, pos=False):
        # new_gr = gr[:]
        # gr_neg = gr
        # pat = pat
        # pat_neg = pat
        if not pos:
            patterns = [None]*2
            incr = row[0]
            if incr > 0:
                temp = tuple([attr, '+'])
                pat[0].append(temp)
                if incr < pat[1][:]:
                    pat[1] = incr
                patterns[0] = pat
            return Trenc.combine_patterns_test2(patterns, row, attr, pos=True)
        else:
            cp = pat[0][:]
            # gr = cp[1]
            temp = tuple([attr, '+'])
            cp[0].remove(temp) if cp[0] else cp[0]

            decr = row[1]
            if decr > 0:
                temp = tuple([attr, '-'])
                cp[0].append(temp)
                if decr < cp[1][:]:
                    cp[1] = decr
                pat[1] = cp
            return pat

    @staticmethod
    def combine_patterns_test(pat, row, attr, sign, gr):
        gr_pos = gr
        gr_neg = gr
        pat_pos = pat
        pat_neg = pat
        incr = row[0]
        decr = row[1]

        if incr > 0:
            temp = tuple([attr, '+'])
            pat_pos.append(temp)
            if incr < gr_pos:
                gr_pos = incr
        else:
            pat_pos = []
            gr_pos = 0

        if decr > 0:
            temp = tuple([attr, '-'])
            pat_neg.append(temp)
            if decr < gr_neg:
                gr_neg = decr
        else:
            pat_neg = []
            gr_neg = 0
        return [pat_pos, gr_pos], [pat_neg, gr_neg]

    @staticmethod
    def combine_patterns_test1(pat, row, attr, sign):
        if sign == '+':
            dir_ = row[0]
        elif sign == '-':
            dir_ = row[1]
        else:
            return [], 0
        if dir_ > 0:
            temp = tuple([attr, sign])
            pat[0].append(temp)
            if dir_ < pat[1]:
                pat[1] = dir_
            return pat
        else:
            return []

    @staticmethod
    def gen_GR_matrix(ds_id, gp_list):
        GR_list = list()
        if ds_id < len(gp_list):
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
                    # print(str([temp, GR_matrix, matrix]) + "\n")
                    GR = [temp, gp_1.extracted_patterns, gp_2.extracted_patterns]
                    GR_list.append(GR)
            return GR_list
        else:
            raise Exception("Selected data-set/file does not exist")

    @staticmethod
    def fetch_csv_data(path):
        d_set = HandleData(path)
        if d_set.data:
            d_set.init_attributes(eq=False)
            # print(d_set.attr_data)
            return d_set
        else:
            return False

    @staticmethod
    def test_titles(title_1, titles_2):
        for item_2 in titles_2:
            title_2 = item_2[1]
            if title_1[1] == title_2:
                return True
        return False

    @staticmethod
    def test_paths(path_str):
        try:
            path_list = [x.strip() for x in path_str.split(',')]
            for path in path_list:
                if path == '':
                    path_list.remove(path)
            path_list = list(dict.fromkeys(path_list))
            return path_list
        except ValueError:
            return list(path_str)
