
from src.algorithms.trenc.trenc import Trenc


def init_trenc(paths, min_sup=0.5, ref_item=1, cores=0, allow_para=0, min_rep=0.5):
    wr_line = ""
    # ep_set = Trenc(paths, 0.5)
    ep_set = Trenc(paths, min_sup, cores, allow_para, min_rep, ref_item)
    ep_list, jep_list = ep_set.run_trenc(0)

    titles = ep_set.titles
    if ref_item is not None:
        for txt in titles:
            col = int(txt[0])
            if col == ref_item:
                wr_line += (str(col) + '. ' + str(txt[1]) + '**' + '\n')
            else:
                wr_line += (str(col) + '. ' + str(txt[1]) + '\n')
    else:
        for txt in titles:
            wr_line += (str(txt[0]) + '. ' + str(txt[1]) + '\n')

    if len(ep_list) < 1 and jep_list < 1:
        wr_line += 'No emerging patterns found\n'
    else:
        for ep in ep_list:
            wr_line += str(ep.pattern_info) + '\n'
        for jep in jep_list:
            wr_line += str(jep.pattern_info) + '\n'
    wr_line += '\n\n --- end --- \n\n RAW PATTERNS\n'
    for obj in ep_set.GR_list:
        wr_line += str(obj[1].extracted_patterns) + '\n'
        wr_line += str(obj[2].extracted_patterns) + '\n'
        wr_line += '\n\n'
    print(wr_line)


init_trenc('../data/DATASET.csv')
