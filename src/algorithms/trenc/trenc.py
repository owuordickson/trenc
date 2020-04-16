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
from src.algorithms.trenc.ep import EP, JEP


class Trenc:

    def __init__(self, f_paths, min_sup, cores=0, allow_para=1, min_rep=None, ref_item=None):
        self.temporal = False
        self.file_paths = Trenc.test_paths(f_paths)
        self.ref_item = ref_item
        self.min_rep = min_rep
        self.min_sup = min_sup
        self.titles = []
        self.GR_list = []

        if cores > 1:
            self.cores = cores
        else:
            self.cores = InitParallel.get_num_cores()

        if allow_para == 0:
            self.allow_parallel = False
            self.msg_para = "False"
        else:
            self.allow_parallel = True
            self.msg_para = "True"

        self.d_sets = self.get_csv_data()
        if len(self.d_sets) <= 1:
            # if we are mining TGPs
            if self.min_rep is None:
                raise Exception("min_representativity and/or reference column required")
            elif self.min_rep is not None:
                d_set = self.d_sets[0]
                self.tg_set = TgradACO(d_set, self.ref_item, self.min_sup, self.min_rep, 0)
                self.d_sets = self.get_transform_data()
                self.temporal = True

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
            if len(d_sets) > 0:
                return d_sets
            else:
                raise Exception("No transformed data set, reduce min_rep")
        else:
            d_sets = list()
            for step in range(self.tg_set.max_step):
                d_set = self.fetch_transform_data(step)
                d_sets.append(d_set)
            if len(d_sets) > 0:
                return d_sets
            else:
                raise Exception("No transformed data set, reduce min_rep")

    def run_trenc(self, set_id=0):
        # test titles
        ok = self.compare_ds_titles()
        if not ok:
            raise Exception("Data sets have different columns")
        else:
            gp_list = self.fetch_patterns()
            self.GR_list = Trenc.gen_GR_matrix(set_id, gp_list)
            eps, jeps = Trenc.construct_eps(self.GR_list)
            return eps, jeps

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
                    # normalize stamp_matrix
                    gp_2.tstamp_matrix = Trenc.remove_useless_stamps(temp, gp_2.tstamp_matrix)
                    GR = [temp, gp_1, gp_2]
                    GR_list.append(GR)
            return GR_list
        else:
            raise Exception("Selected data-set/file does not exist")

    @staticmethod
    def remove_useless_stamps(GR_matrix, stamp_matrix):
        if not stamp_matrix:
            return stamp_matrix
        else:
            size = len(GR_matrix)
            for i in range(size):
                row = GR_matrix[i]
                if row[0] == 0:
                    stamp_matrix[i][0] = []
                if row[1] == 0:
                    stamp_matrix[i][1] = []
            return stamp_matrix

    @staticmethod
    def construct_eps(GR_list):
        eps = list()
        jeps = list()
        raw_ep1 = False
        for GR in GR_list:
            GR_matrix = GR[0]
            gp1_stamps = GR[1].tstamp_matrix
            gp2_stamps = GR[2].tstamp_matrix
            if not gp1_stamps:
                temp_eps, temp_jeps = Trenc.construct_gps(GR_matrix)
                for ep in temp_eps:
                    eps.append(ep)
                for jep in temp_jeps:
                    jeps.append(jep)
            else:
                # eps, jeps = Trenc.construct_tgps1(GR_matrix, gp1_stamps, gp2_stamps)
                if not raw_ep1:
                    ok, raw_ep1 = Trenc.construct_tgps(GR_matrix, gp1_stamps)
                if raw_ep1:
                    raw_ep1, raw_ep2 = Trenc.construct_tgps(GR_matrix, gp2_stamps, ep=raw_ep1)
        if raw_ep1:
            temp_eps, temp_jeps = Trenc.fetch_eps(raw_ep1)
            for ep in temp_eps:
                eps.append(ep)
            for jep in temp_jeps:
                jeps.append(jep)
        return eps, jeps

    @staticmethod
    def fetch_eps(raw_ep):
        eps = list()
        jeps = list()
        for pat in raw_ep:
            count = len(pat)
            if count == 2:
                # this a 'Jumping Emerging Pattern'
                gp = pat[0]
                t_lag1 = pat[1]
                jep = JEP(gp, t_lag1)
                jeps.append(jep)
            else:
                # a normal 'Emerging Pattern'
                gp = pat[0]
                t_lag1 = pat[1]
                t_lags = []
                for i in range(2, count, 1):
                    t_lags.append(pat[i])
                ep = EP(gp, 0, t_lag1, t_lags)
                eps.append(ep)
        return eps, jeps

    @staticmethod
    def construct_gps(GR_matrix):
        eps = list()
        jeps = list()
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

            if incr > 1 or incr == -1:
                pat = [[tuple([attr, '+'])], incr]
                for j in range(i+1, size, 1):
                    row_j = GR_matrix[j]
                    pat = Trenc.combine_patterns(pat, row_j, j)
                if len(pat[0]) > 1:
                    if pat[1] == -1:
                        jep = JEP(pat[0])
                        jeps.append(jep)
                    else:
                        ep = EP(pat[0], pat[1])
                        eps.append(ep)

            if decr > 1 or decr == -1:
                pat = [[tuple([attr, '-'])], decr]
                for j in range(i+1, size, 1):
                    row_j = GR_matrix[j]
                    pat = Trenc.combine_patterns(pat, row_j, j)
                if len(pat[0]) > 1:
                    if pat[1] == -1:
                        jep = JEP(pat[0])
                        jeps.append(jep)
                    else:
                        ep = EP(pat[0], pat[1])
                        eps.append(ep)
        # print([ep, jep])
        return eps, jeps

    @staticmethod
    def construct_tgps(GR_matrix, gp_tstamps, ep=None):
        tgp = []
        size = len(GR_matrix)
        gp_stamps = gp_tstamps
        for i in range(size):
            row = gp_stamps[i]
            for j in range(len(row)):
                # gr = GR_matrix[i][j]
                col = row[j]
                for t_stamp in col:
                    pat, gr, gp1_stamps = Trenc.find_same_stamps(t_stamp, gp_stamps, GR_matrix)
                    pattern = [pat, t_stamp]
                    if pat and (pattern not in tgp):
                        tgp.append(pattern)
                        if ep is not None:
                            for k in range(len(ep)):
                                obj = ep[k]
                                pat1 = obj[0]
                                if sorted(pat1) == sorted(pat):
                                    ep[k].append([t_stamp, gr])
        if ep is None:
            return False, tgp
        else:
            return ep, tgp

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
            temp = tuple([attr, sign])
            pat[0].append(temp)
            if dir_ < pat[1]:
                pat[1] = dir_
            return pat
        else:
            return []

    @staticmethod
    def find_same_stamps(t_stamp, stamp_matrix, GR_matrix):
        attrs = list()
        patterns = []
        gr = 0
        size = len(stamp_matrix)
        for i in range(size):
            attr = i
            row = stamp_matrix[i]
            for j in range(len(row)):
                stamps = stamp_matrix[i][j]
                if t_stamp in stamps:
                    # print([t_stamp, stamps, 'true'])
                    if j == 0:
                        sign = '+'
                    elif j == 1:
                        sign = '-'
                    else:
                        continue
                    pat = tuple([attr, sign])
                    if (pat not in patterns) and (attr not in attrs):
                        attrs.append(attr)
                        patterns.append(pat)
                        temp_gr = GR_matrix[i][j]
                        gr = temp_gr if (gr == 0) or (temp_gr < gr) else gr
                    stamp_matrix[i][j].remove(t_stamp)
        if len(patterns) > 1:
            return patterns, gr, stamp_matrix
        else:
            return False, gr, stamp_matrix

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
