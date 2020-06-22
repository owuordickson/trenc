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
        tgeps = None
        for GR in GR_list:
            GR_matrix = GR[0]
            gp1_stamps = GR[1].tstamp_matrix
            gp2_stamps = GR[2].tstamp_matrix

            if tgeps is None:
                tgeps = Trenc_TGP.construct_tgps(GR_matrix, gp1_stamps)
            if tgeps is not None:
                tgeps = Trenc_TGP.construct_tgps(GR_matrix, gp2_stamps, ep=tgeps)
        return tgeps

    @staticmethod
    def construct_tgps(GR_matrix, gp_stamps, ep=None):
        tgp = []
        temp_pats = list()
        size = len(GR_matrix)
        for i in range(size):  # all attributes
            for j in range(2):  # same as p_matrix: + or -
                # gr = GR_matrix[i][j]
                col_stamps = gp_stamps[i][j]
                for t_stamp in col_stamps:
                    pat, gr, gp_stamps = Trenc_TGP.find_same_stamps(t_stamp, gp_stamps, GR_matrix)
                    if not pat:
                        continue
                    pattern = TGEP(pat, t_lag=TimeLag(tstamp=t_stamp[0], supp=t_stamp[1]))
                    if pat.get_tuples() not in temp_pats:
                        temp_pats.append(pat.get_tuples())
                        tgp.append(pattern)
                        if ep is not None:
                            for k in range(len(ep)):
                                obj = ep[k]
                                pat1 = obj.get_pattern()  # obj[0]
                                if sorted(pat1) == sorted(pat.get_pattern()):
                                    ep[k].add_timestamp(t_stamp[0], t_stamp[1], gr)
        if ep is None:
            return tgp
        else:
            return ep

    @staticmethod
    def find_same_stamps(t_stamp, stamp_matrix, GR_matrix):
        attrs = list()
        patterns = GP()
        gr = 0
        size = len(stamp_matrix)
        for i in range(size):
            attr = i
            for j in range(2):  # similar to p_matrix
                stamps = stamp_matrix[i][j]
                if t_stamp in stamps:
                    # print([t_stamp, stamps, 'true'])
                    if j == 0:
                        sign = '+'
                    else:
                        sign = '-'
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
