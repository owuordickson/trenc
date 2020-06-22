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
from src.trenc.algorithms.hdf5.trenc_gp_h5 import Trenc_GP_h5
from src.trenc.algorithms.hdf5.trenc_tgp_h5 import Trenc_TGP_h5


def init_trenc(paths, minSup, ref_item, ref_dset, cores, allow_para, minRep):
    try:
        if minRep == 0:
            ep_set = Trenc_GP_h5(paths, minSup, ref_dset, cores, allow_para)
        else:
            ep_set = Trenc_TGP_h5(paths, minSup, minRep, ref_item, ref_dset, cores, allow_para)
        gep_list = ep_set.run_trenc()

        wr_line = "Algorithm: TRENC \n"
        if minRep == 0:
            wr_line += "Pattern Type: Gradual Emerging Patterns\n"
            wr_line += "No. of data sets: " + str(len(ep_set.d_sets)) + '\n'
            wr_line += "Size of 1st data set: " + str(ep_set.d_sets[0].size) + '\n'
        else:
            wr_line += "Pattern Type: Temporal Gradual Emerging Patterns\n"
            wr_line += "No. of data sets: " + str(ep_set.tg_set.max_step) + '\n'
            wr_line += "Size of 1st data set: " + str(ep_set.tg_set.d_set.size) + '\n'
        wr_line += "No. of (data set) attributes: " + str(len(ep_set.titles)) + '\n'
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
            if min_rep == 0:
                for obj in gep_list:
                    if obj:
                        for ep in obj:
                            wr_line += str(ep.jsonify()) + '\n'
            else:
                for ep in gep_list:
                    wr_line += str(ep.jsonify()) + '\n'
        wr_line += '\n\n --- end --- \n\n '
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
        ref_ds = sys.argv[5]
        allow_p = sys.argv[6]
        num_cores = 1
    else:
        optparser = OptionParser()
        optparser.add_option('-f', '--inputFile',
                             dest='file',
                             help='path to file containing csv',
                             # default=None,
                             #default='../../data/DATASET.csv',
                             default='../../data/ICU_household_power_consumption1.csv',
                             #default='../../data/DATASET.csv, ../../data/DATASET1.csv',
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
        optparser.add_option('-d', '--refDataset',
                             dest='refDset',
                             help='reference data set',
                             default=0,
                             type='int')
        optparser.add_option('-p', '--allowMultiprocessing',
                             dest='allowPara',
                             help='allow multiprocessing',
                             default=0,
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
        ref_ds = options.refDset
        allow_p = options.allowPara
        num_cores = options.numCores

    import time
    start = time.time()
    res_text = init_trenc(file_path, min_sup, ref_col, ref_ds, num_cores, allow_p, min_rep)
    end = time.time()

    wr_text = ("Run-time: " + str(end - start) + " seconds\n")
    wr_text += str(res_text)
    f_name = str('res_trenc' + str(end).replace('.', '', 1) + '.txt')
    # write_file(wr_text, f_name)
    print(wr_text)
