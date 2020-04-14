"""
@author: "Dickson Owuor"
@credits: "Joseph Orero and Anne Laurent,"
@license: "MIT"
@version: "2.0"
@email: "owuordickson@gmail.com"
@created: "19 November 2019"

Usage:
    $python init_bordertgraank.py -t pType -f fileName.csv -c refCol -s minSup  -r minRep

Description:
    f -> file path (CSV)
    c -> reference column
    s -> minimum support
    r -> representativity

"""

import sys
from optparse import OptionParser
from src.algorithms.border_ep.mbdll_border import *
from src.algorithms.border_ep.border_tgraank import *


def algorithm_ep_init(filename, ref_item, minsup, minrep, cores):
    try:
        wr_line = ''
        fgp_list = list()  # fuzzy-temporal gradual patterns

        # 1. Load dataset into program
        dataset = DataTransform(filename, ref_item, minrep)

        # 2. TRANSFORM DATA (for each step)
        for s in range(dataset.max_step):
            step = s+1  # because for-loop is not inclusive from range: 0 - max_step
            # 3. Calculate representativity
            chk_rep, rep_info = dataset.get_representativity(step)

            if chk_rep:
                # 4. Transform data
                data, time_diffs = dataset.transform_data(step)

                # 5. Execute GRAANK for each transformation
                title, gp_list, sup_list, tlag_list = graank(trad(list(data)), minsup, time_diffs, eq=False)

                pattern_found = check_for_pattern(ref_item, gp_list)
                if pattern_found:
                    maximal_items = get_maximal_items(gp_list, tlag_list)
                    fgp_list.append(tuple((title, maximal_items)))
        if not fgp_list:
            wr_line += "Oops! no frequent patterns were found\n"
            # wr_line += "-------------------------------------"
        else:
            wr_line = "Algorithm: Border-TGRAANK \n"
            wr_line += "No. of data sets: " + str(dataset.max_step) + '\n'
            wr_line += "No. of (dataset) attributes: " + str(len(dataset.data[0])) + '\n'
            wr_line += "Minimum support: " + str(minsup) + '\n'
            wr_line += "Minimum representativity: " + str(minrep) + '\n'
            # wr_line += "Multi-core execution: " + str(ep_set.msg_para) + '\n'
            wr_line += "Number of cores: " + str(cores) + '\n'
            wr_line += '\n\n'

            for line in title:
                wr_line += line + '\n'
            wr_line += 'Emerging Pattern | Time Lags: (Transformation n, Transformation m)\n\n'

            all_fgps = list()
            for item_list in fgp_list:
                for item in item_list[1]:
                    all_fgps.append(item)

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
    except Exception as error:
        wr_line = "Failed: " + str(error)
        print(error)
        return wr_line


if __name__ == "__main__":

    if not sys.argv:
        pattern_type = sys.argv[1]
        file_name = sys.argv[2]
        ref_col = sys.argv[3]
        min_sup = sys.argv[4]
        min_rep = sys.argv[5]
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
        num_cores = options.numCores

    # import timeit
    # if pattern_type == 1:
    #    algorithm_init(file_name, ref_col, min_sup, min_rep)
    # else:
    import time

    start = time.time()
    # res_text = init_trenc(file_path, min_sup, ref_col, numCores, allow_p, min_rep)
    res_text = algorithm_ep_init(file_name, ref_col, min_sup, min_rep, num_cores)
    end = time.time()

    wr_text = ("Run-time: " + str(end - start) + " seconds\n")
    wr_text += str(res_text)
    f_name = str('res_border' + str(end).replace('.', '', 1) + '.txt')
    # HandleData.write_file(wr_text, f_name)
    print(wr_text)
