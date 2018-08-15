import os
import sys
import io

file = sys.argv[1]

#Get rid of repeating lines
with open(file, 'rb') as f1:
    arr = f1.readlines()
    with open("temp.txt", 'w+') as f2:
        for e in xrange(0, len(arr)):
            if arr[e] not in arr[e+1:]:
                f2.write(arr[e])
os.rename("temp.txt", file)
