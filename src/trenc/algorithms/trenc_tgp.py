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
from ...common.gp import GI, GP, TimeLag
from ...common.ep import TGEP
from ...common.ep_old import EP, JEP
from ...common.profile_cpu import Profile


class Trenc_TGP(Trenc_GP):

    def __init__(self, f_paths, min_sup, min_rep, ref_item, cores=0, allow_para=1):
        self.ref_item = ref_item
        self.min_rep = min_rep
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
        self.GR_list = []

        d_set = self.get_dataset(f_paths)
        self.tg_set = T_GradACOgr(d_set, ref_item, min_rep, self.cores)
        self.titles = d_set.title

    def run_trenc(self, set_id=0):
        tgp_list = self.tg_set.run_tgraank(self.allow_parallel)
        GR_list = Trenc_TGP.gen_GR_matrix(set_id, tgp_list)
        tgeps = Trenc_TGP.construct_tgeps(GR_list)
        return tgeps

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
    def construct_tgeps(GR_list):
        eps = list()
        jeps = list()
        raw_ep1 = None
        for GR in GR_list:
            GR_matrix = GR[0]
            gp1_stamps = GR[1].tstamp_matrix
            gp2_stamps = GR[2].tstamp_matrix

            if raw_ep1 is None:
                ok, raw_ep1 = Trenc_TGP.construct_tgps(GR_matrix, gp1_stamps)
            if raw_ep1 is not None:
                raw_ep1, raw_ep2 = Trenc_TGP.construct_tgps(GR_matrix, gp2_stamps, ep=raw_ep1)

        if raw_ep1 is not None:
            temp_eps, temp_jeps = Trenc_TGP.fetch_eps(raw_ep1)
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
            count = len(pat.gradual_items)
            if count == 2:
                # this a 'Jumping Emerging Pattern'
                gp = pat #pat[0]
                t_lag1 = pat.time_lag #pat[1]
                jep = JEP(gp, t_lag1)
                jeps.append(jep)
            else:
                # a normal 'Emerging Pattern'
                gp = pat # pat[0]
                t_lag1 = pat.time_lag # pat[1]
                t_lags = pat.gr_timelags #[]
                #for i in range(2, count, 1):
                #    t_lags.append(pat[i])
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
                    pat, gr, gp1_stamps = Trenc_TGP.find_same_stamps(t_stamp, gp_stamps, GR_matrix)
                    if not pat:
                        continue
                    pattern = TGEP(pat, t_lag=TimeLag(tstamp=t_stamp[0], supp=t_stamp[1]))
                    if pattern not in tgp:
                        tgp.append(pattern)
                        if ep is not None:
                            for k in range(len(ep)):
                                obj = ep[k]
                                pat1 = obj.get_pattern()  # obj[0]
                                if sorted(pat1) == sorted(pat.get_pattern()):
                                    ep[k].add_timestamp(t_stamp[0], t_stamp[1], gr)
                                    # ep[k].append([t_stamp, gr])
        if ep is None:
            return False, tgp
        else:
            return ep, tgp

    @staticmethod
    def find_same_stamps(t_stamp, stamp_matrix, GR_matrix):
        attrs = list()
        patterns = GP()
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
                    gi = GI(attr, sign)
                    if (gi not in patterns.gradual_items) and (attr not in attrs):
                        attrs.append(attr)
                        patterns.add_gradual_item(gi)
                        temp_gr = GR_matrix[i][j]
                        gr = temp_gr if (gr == 0) or (temp_gr < gr) else gr
                    stamp_matrix[i][j].remove(t_stamp)
        if len(patterns.gradual_items) > 1:
            return patterns, gr, stamp_matrix
        else:
            return False, gr, stamp_matrix
