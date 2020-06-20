"""
@author: "Dickson Owuor"
@credits: "Joseph Orero and Anne Laurent,"
@license: "MIT"
@version: "2.0"
@email: "owuordickson@gmail.com"
@created: "19 November 2019"
@modified: "13 May 2020"

Usage:
    $python3 init_bordertgraank.py -f fileName.csv -c refCol -s minSup  -r minRep

Description:
    f -> file path (CSV)
    c -> reference column
    s -> minimum support
    r -> representativity

"""

import sys
from optparse import OptionParser
from src.border_ep.algorithms.mbdll_border import *
from src.border_ep.algorithms.border_tgraank import *
from src.border_ep.algorithms.t_graank import Tgraank


def algorithm_ep_init(filename, ref_item, minsup, minrep, cores, allow_para):
    try:
        wr_line = ''
        fgp_list = list()  # fuzzy-temporal gradual patterns

        # 1. Load dataset into program
        dataset = DataTransform(filename, ref_item, minrep)
        tgp = Tgraank(dataset, minsup, ref_item, cores, allow_para)
        # 2. TRANSFORM DATA (for each step)
        # for s in range(dataset.max_step):
        fgp_list = tgp.extract_tgps()

        if not fgp_list:
            wr_line += "Oops! no frequent patterns were found\n"
            # wr_line += "-------------------------------------"
        else:
            wr_line = "Algorithm: Border-TGRAANK \n"
            wr_line += "No. of data sets: " + str(dataset.max_step) + '\n'
            wr_line += "No. of (dataset) attributes: " + str(len(dataset.data[0])) + '\n'
            wr_line += "Minimum support: " + str(minsup) + '\n'
            wr_line += "Minimum representativity: " + str(minrep) + '\n'
            wr_line += "Multi-core execution: " + str(tgp.msg_parallel) + '\n'
            wr_line += "Number of cores: " + str(cores) + '\n'
            wr_line += '\n\n'

            for line in tgp.title:
                wr_line += line + '\n'
            wr_line += 'Emerging Pattern | Time Lags: (Transformation n, Transformation m)\n\n'

            all_fgps = list()
            for item_list in fgp_list:
                if len(item_list) > 0:
                    for item in item_list[1]:
                        all_fgps.append(item)
                else:
                    continue

            patterns = 0
            ep_list = list()
            for i in range(len(all_fgps)):
                for j in range(i, len(all_fgps)):
                    if i != j:
                        freq_pattern_1 = all_fgps[i]
                        freq_pattern_2 = all_fgps[j]
                        ep = mbdll_border(tuple(freq_pattern_1[0]), tuple(freq_pattern_2[0]))
                        tlags = tuple((freq_pattern_1[1], freq_pattern_2[1]))
                        if ep:
                            patterns = patterns + 1
                            temp = tuple((ep, tlags))
                            ep_list.append(temp)
                            wr_line += str(temp[0]) + " | " + str(temp[1]) + '\n'

            wr_line += "\nTotal: " + str(patterns) + " FtGEPs found!\n"
            # wr_line += "---------------------------------------------------------"
            if patterns == 0:
                wr_line += "Oops! no relevant emerging pattern was found\n\n"
                # wr_line += "---------------------------------------------------------"
        return wr_line
    except ArithmeticError as error:
        wr_line = "Failed: " + str(error)
        print(error)
        return wr_line


def write_file(data, path):
    with open(path, 'w') as f:
        f.write(data)
        f.close()


if __name__ == "__main__":

    if not sys.argv:
        pattern_type = sys.argv[1]
        file_name = sys.argv[2]
        ref_col = sys.argv[3]
        min_sup = sys.argv[4]
        min_rep = sys.argv[5]
        num_cores = 1
    else:
        optparser = OptionParser()
        optparser.add_option('-t', '--patternType',
                             dest='pType',
                             help='patterns: FtGP, FtGEP',
                             default=1,
                             type='int')
        optparser.add_option('-f', '--inputFile',
                             dest='file',
                             help='path to file containing csv',
                             # default=None,
                             default='../data/DATASET.csv',
                             type='string')
        optparser.add_option('-c', '--refColumn',
                             dest='refCol',
                             help='reference column',
                             default=0,
                             type='int')
        optparser.add_option('-s', '--minSupport',
                             dest='minSup',
                             help='minimum support value',
                             default=0.5,
                             type='float')
        optparser.add_option('-r', '--minRepresentativity',
                             dest='minRep',
                             help='minimum representativity',
                             default=0.5,
                             type='float')
        optparser.add_option('-p', '--allowMultiprocessing',
                             dest='allowPara',
                             help='allow multiprocessing',
                             default=1,
                             type='int')
        optparser.add_option('-m', '--cores',
                             dest='numCores',
                             help='number of cores',
                             default=4,
                             type='int')
        (options, args) = optparser.parse_args()

        inFile = None
        if options.file is None:
            print('No data-set filename specified, system with exit')
            print("Usage: $python init_bordertgraank.py -f filename.csv -c refColumn -s minSup  -r minRep")
            sys.exit('System will exit')
        else:
            inFile = options.file

        file_name = inFile
        pattern_type = options.pType
        ref_col = options.refCol
        min_sup = options.minSup
        min_rep = options.minRep
        allow_p = options.allowPara
        num_cores = options.numCores

    # import timeit
    # if pattern_type == 1:
    #    algorithm_init(file_name, ref_col, min_sup, min_rep)
    # else:
    import time

    start = time.time()
    # res_text = init_trenc(file_path, min_sup, ref_col, numCores, allow_p, min_rep)
    res_text = algorithm_ep_init(file_name, ref_col, min_sup, min_rep, num_cores, allow_p)
    end = time.time()

    wr_text = ("Run-time: " + str(end - start) + " seconds\n")
    wr_text += str(res_text)
    f_name = str('res_border' + str(end).replace('.', '', 1) + '.txt')
    # write_file(wr_text, f_name)
    print(wr_text)
