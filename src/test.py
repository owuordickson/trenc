def construct_eps(GR_matrix):
    eps = list()
    jeps = list()
    size = len(GR_matrix)
    ep = list()
    jep = list()
    for i in range(size):
        attr = i
        row_i = GR_matrix[i]
        incr = row_i[0]
        decr = row_i[1]
        if incr == -1:
            temp = tuple([attr, '+'])
            jep.append(temp)
        elif incr > 1:
            temp = [tuple([attr, '+']), incr]
            ep.append(temp)
        if decr == -1:
            temp = tuple([attr, '-'])
            jep.append(temp)
        elif decr > 1:
            temp = [tuple([attr, '-']), decr]
            ep.append(temp)
    return eps, jeps


def construct_eps1(GR_matrix):
    eps = list()
    jeps = list()  # coded as -1 in GR_matrix

    ep, jep = Trenc.init_gen_ep(GR_matrix, '+')
    eps.append(ep) if ep else eps
    jeps.append(jep) if jep else jeps

    ep, jep = Trenc.init_gen_ep(GR_matrix, '-')
    eps.append(ep) if ep else eps
    jeps.append(jep) if jep else jeps

    return eps, jeps


def init_gen_ep(GR_matrix, sign):
    size = len(GR_matrix)
    ep = list()
    jep = list()
    # gr = 0
    for i in range(size):
        attr = i
        row_i = GR_matrix[i]
        if sign == '+':
            dir_ = row_i[0]
        elif sign == '-':
            dir_ = row_i[1]
        else:
            return False, False
        if dir_ == -1 and not jep:
            pat = tuple([attr, sign])
            jep.append(pat)
            # continue
        elif dir_ > 0 and not ep:
            pat_pos = [[tuple([attr, sign])], dir_]
            pat_neg = [[tuple([attr, sign])], dir_]
            for j in range( i +1, size, 1):
                row_j = GR_matrix[j]
                pat = Trenc.get_n_set(pat_pos, pat_neg)
                pat_pos = Trenc.combine_patterns_test1(pat_pos, row_j, j, '+')
                pat_neg = Trenc.combine_patterns_test1(pat_neg, row_j, j, '-')
            ep.append(pat_pos)
            ep.append(pat_neg)
            # continue
    ep = False if not ep else ep
    jep = False if not jep else jep
    return ep, jep


def get_n_set(pat_pos, pat_neg):
    pat = list()

    return pat


def combine_patterns_test2(pat, row, attr, pos=False):
    # new_gr = gr[:]
    # gr_neg = gr
    # pat = pat
    # pat_neg = pat
    if not pos:
        patterns = [None ] *2
        incr = row[0]
        if incr > 0:
            temp = tuple([attr, '+'])
            pat[0].append(temp)
            if incr < pat[1][:]:
                pat[1] = incr
            patterns[0] = pat
        return Trenc.combine_patterns_test2(patterns, row, attr, pos=True)
    else:
        cp = pat[0][:]
        # gr = cp[1]
        temp = tuple([attr, '+'])
        cp[0].remove(temp) if cp[0] else cp[0]

        decr = row[1]
        if decr > 0:
            temp = tuple([attr, '-'])
            cp[0].append(temp)
            if decr < cp[1][:]:
                cp[1] = decr
            pat[1] = cp
        return pat


def combine_patterns_test(pat, row, attr, sign, gr):
    gr_pos = gr
    gr_neg = gr
    pat_pos = pat
    pat_neg = pat
    incr = row[0]
    decr = row[1]

    if incr > 0:
        temp = tuple([attr, '+'])
        pat_pos.append(temp)
        if incr < gr_pos:
            gr_pos = incr
    else:
        pat_pos = []
        gr_pos = 0

    if decr > 0:
        temp = tuple([attr, '-'])
        pat_neg.append(temp)
        if decr < gr_neg:
            gr_neg = decr
    else:
        pat_neg = []
        gr_neg = 0
    return [pat_pos, gr_pos], [pat_neg, gr_neg]


def combine_patterns_test1(pat, row, attr, sign):
    if sign == '+':
        dir_ = row[0]
    elif sign == '-':
        dir_ = row[1]
    else:
        return [], 0
    if dir_ > 0:
        temp = tuple([attr, sign])
        pat[0].append(temp)
        if dir_ < pat[1]:
            pat[1] = dir_
        return pat
    else:
        return []


def test_1():
    size_i = 6
    line_pos = ""
    line_neg = ""
    for i in range(size_i):
        size_j = pow(2, i)
        for j in range(size_j):
            if j % 2 == 0:
                line_pos += str(i)+'+'
            else:
                line_neg += str(i)+'-'
        print(line_pos)


def fetch_pats(n, pat, pos=False):
    if not pos:
        pats = [None]*2
        temp = tuple([n, '+'])
        pat.append(temp)
        pats[0] = pat
        return fetch_pats(n, pats, pos=True)
    else:
        cp = pat[0][:]
        temp = tuple([n, '+'])
        cp.remove(temp) if cp else cp
        temp = tuple([n, '-'])
        cp.append(temp)
        pat[1] = cp
        return pat


patterns = fetch_pats(3, list([tuple([1, '+']), tuple([2, '-'])]))
print(patterns)
