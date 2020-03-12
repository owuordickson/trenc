
# from python.algorithms.BorderDiff import *
from algorithms.mbdll_border import *

# testing BORDER-DIFF (python) algorithm

u = set((1, 2, 3, 4))
r = set(((3, 4), (2, 4), (2, 3)))

#u = set(((1, 2, 3, 4), (6, 7, 8)))
#u = set((6, 7, 8))
#r = set((4, 6, 7))
L, U, R = border_diff(tuple(u), tuple(r))

u = set(('rice','beans','sugar','bread'))
r = set((('sugar','bread'), ('beans','bread'), ('beans','sugar')))
#L, U, R = border_diff(tuple(u), tuple(r))

print("U border:" + str(U))
print("R border:" + str(R))
print("L border:"+str(L))

print("")

# testing MBD-LLBORDER (python) algorithm

freqMaxD1 = set(((2, 3, 5), (3, 4, 6, 7, 8), (2, 4, 5, 8, 9)))
freqMaxD2 = set(((1, 2, 3, 4), (6, 7, 8)))

freqMaxD1 = set((('bread', 'milk', 'butter'), ('milk', 'coffee', 'salt', 'sauce', 'cheese'),
                 ('bread', 'coffee', 'butter', 'cheese', 'water')))
freqMaxD2 = set((('sugar', 'bread', 'milk', 'coffee'), ('salt', 'sauce', 'cheese')))

ep_list = mbdll_border(tuple(freqMaxD2), tuple(freqMaxD1))

print("Frequent patterns in D1:"+str(freqMaxD1))
print("Frequent patterns in D2:"+str(freqMaxD2))
print("Emerging patterns D2->D1:")
print("-------------------------")

for i in range(len(ep_list)):
    print("Emerging Pattern" + str(i+1) + ": " + str(set(ep_list[i])))

