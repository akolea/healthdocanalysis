import os
import io
import sys
import plac

s="*ServiceOutput*"
e="*EOBentries*"
t="*temp*.jpg"
d="*doc*.pdf"
w="whatkind.txt"
n1 = "NLPHORIZONTALS.txt"
n2 = "NLPSERVICELINES.txt"
with open("dirname.txt", 'w+') as f1:
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1])
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + s)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + e)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + t)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + d)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + w)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + n1)
    f1.write('\n')
    f1.write(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + n2)
