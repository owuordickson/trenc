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
from .trenc_gp import Trenc_GP
from .aco_tgrad_gr import T_GradACOgr
from ...common.ep_old import EP, JEP
from ...common.profile_cpu import Profile


class Trenc_TGP(Trenc_GP):

    def __init__(self, f_paths, min_sup, cores=0, allow_para=1, min_rep=None, ref_item=None):

        self.ref_item = ref_item
        self.min_rep = min_rep
        self.min_sup = min_sup
        self.titles = []
        self.GR_list = []

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

        d_set = self.get_csv_data(f_paths)
        self.tg_set = T_GradACOgr(d_set, self.ref_item, self.min_sup, self.min_rep, 0)

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
                            ok = Trenc_GP.test_titles(title_1, titles_2)
                            if not ok:
                                return False
            self.titles = self.d_sets[0].title
            return True

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
                    gp_2.tstamp_matrix = Trenc_TGP.remove_useless_stamps(temp, gp_2.tstamp_matrix)
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
        raw_ep1 = None
        for GR in GR_list:
            GR_matrix = GR[0]
            gp1_stamps = GR[1].tstamp_matrix
            gp2_stamps = GR[2].tstamp_matrix
            if not gp1_stamps:
                temp_eps, temp_jeps = Trenc_GP.construct_gps(GR_matrix)
                for ep in temp_eps:
                    eps.append(ep)
                for jep in temp_jeps:
                    jeps.append(jep)
            else:
                # eps, jeps = Trenc.construct_tgps1(GR_matrix, gp1_stamps, gp2_stamps)
                if raw_ep1 is None:
                    ok, raw_ep1 = Trenc_GP.construct_tgps(GR_matrix, gp1_stamps)
                if raw_ep1 is not None:
                    raw_ep1, raw_ep2 = Trenc_GP.construct_tgps(GR_matrix, gp2_stamps, ep=raw_ep1)
        if raw_ep1 is not None:
            temp_eps, temp_jeps = Trenc_GP.fetch_eps(raw_ep1)
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
                    pat, gr, gp1_stamps = Trenc_GP.find_same_stamps(t_stamp, gp_stamps, GR_matrix)
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
