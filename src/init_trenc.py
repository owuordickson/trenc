
from src.algorithms.trenc.trenc import Trenc


def init_trenc(paths):
    # ep_set = Trenc(paths, 0.5)
    ep_set = Trenc(paths, 0.5, cores=0, allow_para=0, min_rep=0.5, ref_item=1)
    # print(ep_set.d_sets)
    ep_set.run_trenc()


init_trenc('../data/DATASET.csv')
