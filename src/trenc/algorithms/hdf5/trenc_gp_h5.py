# -*- coding: utf-8 -*-
"""
@author: "Dickson OWUOR"
@credits: "Anne LAURENT, Joseph ORERO"
@version: "2.0"
@email: "owuordickson@gmail.com"
@created: "17 March 2020"

TRENC: Temporal gRadual Emerging aNt Colony optimization
This algorithm implements and modifies

"""

import multiprocessing as mp
import numpy as np
from ..trenc_gp import Trenc_GP
from ....common.hdf5.dataset_h5 import Dataset_h5
from .aco_grad_gr_h5 import GradACOgr_h5
from ....common.profile_cpu import Profile


class Trenc_GP_h5(Trenc_GP):

    def __init__(self, f_paths, min_sup, ref_dset_id, cores=0, allow_para=1):
        self.paths = Trenc_GP.get_paths(f_paths)
        if len(self.paths) < 2:
            raise Exception("File Path Error: less than 2 paths found")
        else:
            self.min_sup = min_sup
            self.ref_ds_id = ref_dset_id
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
            self.ref_dset = []
            self.d_sets = self.get_csv_data()
            if len(self.d_sets) <= 1:
                # Not possible to mine EPs
                raise Exception("Mining EPs requires at least 2 data sets")

    def get_dataset(self, path):
        d_set = Dataset_h5(path, self.min_sup, eq=False)
        d_set.init_attributes()
        return d_set

    @staticmethod
    def extract_gps(d_set):
        ac = GradACOgr_h5(d_set)
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
