
from src.algorithms.trenc.trenc import Trenc


def init_trenc(paths):
    ep_set = Trenc(paths, 0.5)
    print(ep_set.d_sets)


init_trenc('../data/DATASET.csv')
