
from src.algorithms.trenc.trenc import Trenc


def init_trenc(paths, min_sup=0.5, cores=0, allow_para=0, min_rep=None, ref_item=None):
    wr_line = ""
    ep_set = Trenc(paths, 0.5)
    # ep_set = Trenc(paths, 0.5, cores=0, allow_para=1, min_rep=0.5, ref_item=1)
    # print(ep_set.d_sets)
    ep_set.run_trenc()

    titles = ep_set.titles
    if ref_item is not None:
        for txt in titles:
            col = (int(txt[0]) - 0)
            if col == ref_item:
                wr_line += (str(txt[0]) + '. ' + str(txt[1]) + '**' + '\n')
            else:
                wr_line += (str(txt[0]) + '. ' + str(txt[1]) + '\n')
    else:
        for txt in titles:
            wr_line += (str(txt[0]) + '. ' + str(txt[1]) + '\n')
    print(wr_line)


init_trenc('../data/DATASET.csv,../data/DATASET.csv')
