
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
        temp = str(n)+'+'
        pat.append(temp)
        pats[0] = pat
        return fetch_pats(n, pats, pos=True)
    else:
        cp = pat[0][:]
        temp = str(n) + '+'
        del cp[-1] if cp else cp
        temp = str(n)+'-'
        cp.append(temp)
        pat[1] = cp
        return pat


patterns = fetch_pats(3, list(['1+', '2-']))
print(patterns)
