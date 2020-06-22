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

from ..trenc_tgp import Trenc_TGP
from .aco_tgrad_gr_h5 import T_GradACOgrH5
from ....common.hdf5.dataset_h5 import Dataset_h5
from ....common.profile_cpu import Profile


class Trenc_TGP_h5(Trenc_TGP):

    def __init__(self, f_paths, min_sup, min_rep, ref_item, ref_dset_id, cores=0, allow_para=1):
        self.paths = Trenc_TGP_h5.get_paths(f_paths)
        if len(self.paths) > 1:
            raise Exception("File Path Error: more than 1 path found")
        else:
            self.ref_item = ref_item
            self.min_rep = min_rep
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

            self.ref_dset = []
            d_set = self.get_dataset(f_paths)
            self.tg_set = T_GradACOgrH5(d_set, ref_item, min_rep, self.cores)
            self.titles = d_set.title

    def get_dataset(self, path):
        d_set = Dataset_h5(path, self.min_sup, eq=False)
        d_set.init_h5_groups()
        return d_set

