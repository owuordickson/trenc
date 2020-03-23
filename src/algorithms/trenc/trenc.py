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
        self.ep_list = []
        self.GR_matrix = []

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
            self.ep_list = self.fetch_patterns()
            self.GR_matrix = self.gen_GR_matrix(set_id)
            for obj in self.ep_list:
                print(obj.extracted_patterns)
                # print(obj.sup_matrix)
                # print("\n")
            print(self.GR_matrix)
            return self.GR_matrix

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
            st_matrix = ac.st_matrix
            # If you don't pass `out` the indices where (b == 0)
            # will be uninitialized!
            sup_matrix = np.divide(p_matrix, st_matrix,
                                   out=np.zeros_like(p_matrix), where=st_matrix != 0)
            ac.sup_matrix = sup_matrix
            return ac
        else:
            raise Exception("one of the data sets is not valid")

    def gen_GR_matrix(self, ds_id):
        ep_list = self.ep_list
        if ds_id < len(ep_list):
            GR_matrix = ep_list[ds_id].sup_matrix
            for ep in ep_list:
                matrix = ep.sup_matrix
                if np.array_equal(GR_matrix, matrix):
                    continue
                else:
                    temp = np.divide(GR_matrix, matrix, out=np.zeros_like(GR_matrix), where=matrix != 0)
                    GR_matrix = temp
            return GR_matrix
        else:
            raise Exception("Selected data-set/ file does not exist")

    def compare_ds_titles(self):
        if self.min_rep is not None:
            self.titles = self.d_sets[0][0].title
            return True
        else:
            for d_set in self.d_sets:
                titles_1 = d_set.title
                for obj_set in self.d_sets:
                    titles_2 = obj_set.title
                    if titles_1 != titles_2:
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
            raise Exception("Problem with representativity: "+str(rep_info))

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
