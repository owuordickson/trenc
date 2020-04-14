
import sys
from optparse import OptionParser
from src.algorithms.trenc.trenc import Trenc
from src.algorithms.trenc.handle_data import HandleData


def init_trenc(paths, minSup, ref_item, cores, allow_para, minRep):
    try:
        wr_line = ""
        # ep_set = Trenc(paths, 0.5)
        ep_set = Trenc(paths, minSup, cores, allow_para, minRep, ref_item)
        ep_list, jep_list = ep_set.run_trenc(0)

        wr_line = "Algorithm: TRENC \n"
        wr_line += "No. of data sets: " + str(len(ep_set.d_sets)) + '\n'
        wr_line += "No. of (data set) attributes: " + str(len(ep_set.titles)) + '\n'
        wr_line += "Minimum support: " + str(minSup) + '\n'
        wr_line += "Minimum representativity: " + str(minRep) + '\n'
        wr_line += "Multi-core execution: " + str(ep_set.msg_para) + '\n'
        wr_line += "Number of cores: " + str(ep_set.cores) + '\n'
        wr_line += '\n\n'

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

        wr_line += str("\nFile: " + paths + '\n')
        wr_line += str("Patterns" + '\n\n')

        if len(ep_list) < 1 and len(jep_list) < 1:
            wr_line += 'No emerging patterns found\n'
        else:
            for ep in ep_list:
                wr_line += str(ep.pattern_info) + '\n'
            for jep in jep_list:
                wr_line += str(jep.pattern_info) + '\n'
        wr_line += '\n\n --- end --- \n\n '
        # wr_line += 'RAW PATTERNS\n'
        # for obj in ep_set.GR_list:
        #    wr_line += str(obj[1].extracted_patterns) + '\n'
        #    wr_line += str(obj[2].extracted_patterns) + '\n'
        #    wr_line += '\n\n'
        # print(wr_line)
        return wr_line
    except Exception as error:
        wr_line = "Failed: " + str(error)
        print(error)
        return wr_line


if __name__ == "__main__":
    if not sys.argv:
        file_path = sys.argv[1]
        ref_col = sys.argv[2]
        min_sup = sys.argv[3]
        min_rep = sys.argv[4]
        allow_p = sys.argv[5]
    else:
        optparser = OptionParser()
        optparser.add_option('-f', '--inputFile',
                             dest='file',
                             help='path to file containing csv',
                             # default=None,
                             default='../data/DATASET.csv',
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
                             type='float')
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
        allow_p = options.allowPara
        num_cores = options.numCores

    import time
    start = time.time()
    res_text = init_trenc(file_path, min_sup, ref_col, num_cores, allow_p, min_rep)
    end = time.time()

    wr_text = ("Run-time: " + str(end - start) + " seconds\n")
    wr_text += str(res_text)
    f_name = str('res_trenc' + str(end).replace('.', '', 1) + '.txt')
    HandleData.write_file(wr_text, f_name)
    # print(wr_text)
