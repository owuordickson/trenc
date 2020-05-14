"""

@email: "owuordickson@gmail.com"
@created: "13 May 2020"

"""
import multiprocessing as mp
from src.algorithms.border_ep.border_tgraank import *
from src.algorithms.trenc.multiprocess import InitParallel


class Tgraank:

    def __init__(self, dataset, minsup, refcol, cores, allow_para):
        self.d_set = dataset
        self.min_sup = minsup
        self.ref_item = refcol
        self.title = ""
        if cores > 1:
            self.cores = cores
        else:
            self.cores = InitParallel.get_num_cores()

        if allow_para == 0:
            self.msg_parallel = "False"
            self.allow_parallel = False
        else:
            self.msg_parallel = "True"
            self.allow_parallel = True

    def extract_tgps(self):
        if self.allow_parallel:
            steps = range(self.d_set.max_step)
            num_cores = self.cores
            pool = mp.Pool(num_cores)
            tgp_list = pool.map(self.fetch_tgps, steps)
            if len(tgp_list) > 0:
                return tgp_list
            else:
                raise Exception("No temporal gradual patterns found")
        else:
            tgp_list = list()
            for step in range(self.d_set.max_step):
                tgp = self.fetch_tgps(step)
                tgp_list.append(tgp)
            if len(tgp_list) > 0:
                return tgp_list
            else:
                raise Exception("No temporal gradual patterns found")

    def fetch_tgps(self, s):
        # tgps = []
        step = s + 1  # because for-loop is not inclusive from range: 0 - max_step
        # 3. Calculate representativity
        chk_rep, rep_info = self.d_set.get_representativity(step)

        if chk_rep:
            # 4. Transform data
            data, time_diffs = self.d_set.transform_data(step)

            # 5. Execute GRAANK for each transformation
            title, gp_list, sup_list, tlag_list = graank(trad(list(data)), self.min_sup, time_diffs, eq=False)
            self.title = title

            pattern_found = check_for_pattern(self.ref_item, gp_list)
            if pattern_found:
                maximal_items = get_maximal_items(gp_list, tlag_list)
                # tgps.append(tuple((title, maximal_items)))
                return tuple((title, maximal_items))
        return []
