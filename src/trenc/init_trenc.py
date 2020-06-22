"""
@author: "Dickson Owuor"
@credits: "Joseph Orero and Anne Laurent,"
@license: "MIT"
@version: "1.0"
@email: "owuordickson@gmail.com"
@created: "02 April 2020"
@modified: "02 June 2020"

Usage:
    $python3 init_trenc.py -f fileName.csv -c refCol -s minSup  -r minRep

Description:
    f -> file path (CSV)
    c -> reference column
    s -> minimum support
    r -> representativity

"""

import sys
from optparse import OptionParser
from src.trenc.algorithms.trenc_gp import Trenc_GP
from src.trenc.algorithms.trenc_tgp import Trenc_TGP


def init_trenc(paths, minSup, ref_item, cores, allow_para, minRep):
    try:
        # wr_line = ""
        # ep_set = Trenc(paths, 0.5)
        if minRep == 0:
            ep_set = Trenc_GP(paths, minSup, cores, allow_para)
        else:
            ep_set = Trenc_TGP(paths, minSup, minRep, ref_item, cores, allow_para)
        gep_list = ep_set.run_trenc(0)

        wr_line = "Algorithm: TRENC \n"
        #wr_line += "No. of data sets: " + str(len(ep_set.d_sets)) + '\n'
        wr_line += "No. of (data set) attributes: " + str(len(ep_set.titles)) + '\n'
        if minRep == 0:
            wr_line += "Size of 1st data set: " + str(ep_set.d_sets[0].size) + '\n'
        #else:
        #    wr_line += "Size of 1st data set: " + str(ep_set.d_sets[0][0].size) + '\n'
        wr_line += "Minimum support: " + str(minSup) + '\n'
        wr_line += "Minimum representativity: " + str(minRep) + '\n'
        wr_line += "Multi-core execution: " + str(ep_set.msg_para) + '\n'
        wr_line += "Number of cores: " + str(ep_set.cores) + '\n'
        wr_line += "Number of patterns: " + str(len(gep_list)) + '\n'
        wr_line += '\n\n'

        titles = ep_set.titles
        if ref_item is not None:
            for txt in titles:
                col = int(txt[0])
                if col == ref_item:
                    wr_line += (str(col) + '. ' + str(txt[1].decode()) + '**' + '\n')
                else:
                    wr_line += (str(col) + '. ' + str(txt[1].decode()) + '\n')
        else:
            for txt in titles:
                wr_line += (str(txt[0]) + '. ' + str(txt[1].decode()) + '\n')

        wr_line += str("\nFiles: " + paths + '\n')
        wr_line += str("Patterns" + '\n\n')

        if len(gep_list) < 1:  # and len(jep_list) < 1:
            wr_line += 'No emerging patterns found\n'
        else:
            for ep in gep_list:
                wr_line += str(ep.jsonify()) + '\n'
        wr_line += '\n\n --- end --- \n\n '
        # wr_line += 'RAW PATTERNS\n'
        # for obj in ep_set.GR_list:
        #    wr_line += str(obj[1].extracted_patterns) + '\n'
        #    wr_line += str(obj[2].extracted_patterns) + '\n'
        #    wr_line += '\n\n'
        # print(wr_line)
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
        file_path = sys.argv[1]
        ref_col = sys.argv[2]
        min_sup = sys.argv[3]
        min_rep = sys.argv[4]
        allow_p = sys.argv[5]
        num_cores = 1
    else:
        optparser = OptionParser()
        optparser.add_option('-f', '--inputFile',
                             dest='file',
                             help='path to file containing csv',
                             # default=None,
                             default='../data/DATASET.csv',
                             #default='../data/DATASET.csv, ../data/DATASET1.csv',
                             #default='../data/rain_temp1991-2015.csv, ../data/rain_temp2013-2015.csv',
                             type='string')
        optparser.add_option('-c', '--refColumn',
                             dest='refCol',
                             help='reference column',
                             default=1,
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
                             #default=0,
                             type='float')
        optparser.add_option('-p', '--allowMultiprocessing',
                             dest='allowPara',
                             help='allow multiprocessing',
                             default=1,
                             type='int')
        optparser.add_option('-m', '--cores',
                             dest='numCores',
                             help='number of cores',
                             default=0,
                             type='int')
        (options, args) = optparser.parse_args()
        inFile = None
        if options.file is None:
            print('No data-set filename specified, system with exit')
            print("Usage: $python3 init_trenc.py -f filename.csv -c refColumn -s minSup  -r minRep")
            sys.exit('System will exit')
        else:
            inFile = options.file
        file_path = inFile
        ref_col = options.refCol
        min_sup = options.minSup
        min_rep = options.minRep
        allow_p = options.allowPara
        num_cores = options.numCores

    import time
    start = time.time()
    res_text = init_trenc(file_path, min_sup, ref_col, num_cores, allow_p, min_rep)
    end = time.time()

    wr_text = ("Run-time: " + str(end - start) + " seconds\n")
    wr_text += str(res_text)
    f_name = str('res_trenc' + str(end).replace('.', '', 1) + '.txt')
    # write_file(wr_text, f_name)
    print(wr_text)
