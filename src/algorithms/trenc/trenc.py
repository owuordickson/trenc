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
from src.algorithms.trenc.multiprocess import InitParallel
from src.algorithms.trenc.handle_data import HandleData
from src.algorithms.trenc.aco_grad import GradACO
from src.algorithms.trenc.aco_t_graank import TgradACO


class Trenc:

    def __init__(self, f_paths, min_sup, cores=0, allow_para=1, min_rep=None, ref_item=None):
        self.file_paths = Trenc.test_paths(f_paths)
        self.ref_item = 1  # ref_item
        self.min_rep = 0.5  # min_rep
        self.min_sup = min_sup

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
                if d_set.data:
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

    def fetch_transform_data(self, step):
        tg_set = self.tg_set
        step += 1  # because for-loop is not inclusive from range: 0 - max_step
        # 1. Calculate representativity
        chk_rep, rep_info = tg_set.get_representativity(step)
        # print(rep_info)
        if chk_rep:
            # 2. Transform data
            data, time_diffs = tg_set.transform_data(step)
            return [data, time_diffs]
        else:
            return False

    def run_trenc(self):
        ep_list = list()
        if self.min_rep is None:
            # run aco-tgrad (single file)
            return ep_list
        else:
            # run aco-grad (multiple files)
            return ep_list

    def extract_eps(self):
        d_sets = self.d_sets
        return None

    @staticmethod
    def fetch_csv_data(path):
        d_set = HandleData(path)
        d_set.init_attributes(eq=False)
        # print(d_set.attr_data)
        return d_set

    @staticmethod
    def test_paths(path_str):
        try:
            path_list = [x.strip() for x in path_str.split(',')]
            for path in path_list:
                if path == '':
                    path_list.remove(path)
            return path_list
        except ValueError:
            return list(path_str)
