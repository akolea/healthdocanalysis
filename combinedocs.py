from __future__ import unicode_literals, print_function
import csv
import io
import os
import numpy
import base64
import sys
import plac
import spacy
import sys
import re
import pandas as pd
import json
import math
import fnmatch
import glob
import sys

reload(sys)
sys.setdefaultencoding('utf8')

prefix = sys.argv[1][sys.argv[1].rfind('/')+1:-4]
#Methods we will need
def isfloat(str):
    try:
        float(str.replace('$','').replace('-','').replace(',','').replace('S',''))
        return True
    except ValueError:
        return False

def isprice(str):
    if isfloat(str) and str.count(".") == 1:
        return True
    else:
        return False

def isitadate(str):
    if str.count("/") == 2 and len(str) < 15:
        return True
    else:
        return False

#Number of ServiceOutput Files
numof = len(glob.glob1(sys.argv[1][0:sys.argv[1].rfind('/') + 1], prefix + "ServiceOutput*"))
allentries = []

for f in xrange(0, numof):
    with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutput"+str(f)+".txt", "rb") as tt:
        allentries.append(tt.readlines())

#Determine document type
isEOB = False
isBill = False
for entry in allentries:
    for ll in entry:
        if "Document Type: EOB" in ll:
            isEOB = True
        if "Document Type: Bill" in ll:
            isBill = True


finalarray = []
foundTotal = False
foundDate = False
foundyou = False
founddd = False
foundcop = False
foundcoi = False
foundadj = False
foundprov = False
servlines = []
copind = 100000
adjind = 100000
totind = 0
#Generates the ServiceOutputFinal.txt for EOB; Note, numerics values add up over pages, as there could be multiple service lines, and values of total and amount owed are summed over service lines
if isEOB:
    finalarray.append("Document Type: EOB\n")
    finalarray.append("Date: N/A\n")
    finalarray.append("Total: N/A\n")
    finalarray.append("You Owe: N/A\n")
    finalarray.append("Deductible: N/A\n")
    finalarray.append("Coinsurance: N/A\n")
    finalarray.append("Copay: N/A")
    finalarray.append("\n\n")
    for entry in allentries:
        for l in xrange(0, len(entry)):
            if 'copay' in entry[l].lower():
                copind = l
                break
        for l in xrange(0, len(entry)):
            if 'total:' in entry[l].lower():
                totind = l
        for l in xrange(0, len(entry)):
            if "Total" in entry[l] and "N/A" not in entry[l] and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if 'N/A' in finalarray[2]:
                    finalarray[2] = entry[l]
                elif isprice(finalarray[2][finalarray[2].index(':') + 2:]):
                    finalarray[2] = "Total: " + str(float(finalarray[2][finalarray[2].index(':') + 2:]) + float(entry[l][entry[l].index(':') + 2:]))
            if "Date" in entry[l] and ':' in entry[l] and isitadate(entry[l][entry[l].index(':'):]) and foundDate == False:
                finalarray[1] = entry[l]
                foundDate = True
            if "You Owe" in entry[l] and "N/A" not in entry[l] and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if 'N/A' in finalarray[3]:
                    finalarray[3] = entry[l]
                elif isprice(finalarray[3][finalarray[3].index(':') + 2:]):
                    finalarray[3] = "You Owe: " + str(float(finalarray[3][finalarray[3].index(':') + 2:]) + float(entry[l][entry[l].index(':') + 2:]))
            if "Deductible" in entry[l] and "N/A" not in entry[l] and ("Total: N/A" not in entry[totind]) and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if 'N/A' in finalarray[4]:
                    finalarray[4] = entry[l]
                elif isprice(finalarray[4][finalarray[4].index(':') + 2:]):
                    finalarray[4] = "Deductible: " + str(float(finalarray[4][finalarray[4].index(':') + 2:]) + float(entry[l][entry[l].index(':') + 2:]))
            if "Coinsurance" in entry[l] and "N/A" not in entry[l] and ("Total: N/A" not in entry[totind]) and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if 'N/A' in finalarray[5]:
                    finalarray[5] = entry[l]
                elif isprice(finalarray[5][finalarray[5].index(':') + 2:]):
                    finalarray[5] = "Coinsurance: " + str(float(finalarray[5][finalarray[5].index(':') + 2:]) + float(entry[l][entry[l].index(':') + 2:]))
            if "Copay" in entry[l] and "N/A" not in entry[l] and ("Total: N/A" not in entry[totind]) and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if 'N/A' in finalarray[6]:
                    finalarray[6] = entry[l]
                elif isprice(finalarray[6][finalarray[6].index(':') + 2:]):
                    finalarray[6] = "Copay: " + str(float(finalarray[6][finalarray[6].index(':') + 2:]) + float(entry[l][entry[l].index(':') + 2:]))
            if l > copind:
                finalarray.append(entry[l])


#Generates the ServiceOutputFinal.txt for Bill; Note that numeric entries across various pages will replace each other, ie. Total is greatest value across all pages
if isBill:
    finalarray.append("Document Type: Bill\n")
    finalarray.append("Date: N/A\n")
    finalarray.append("Provider: N/A\n")
    finalarray.append("Total: N/A\n")
    finalarray.append("Payments and adjustments: N/A\n")
    finalarray.append("\n\n")
    for entry in allentries:
        for l in xrange(0, len(entry)):
            if "Total" in entry[l] and "N/A" not in entry[l] and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                if "N/A" in finalarray[3]:
                    finalarray[3] = entry[l]
                elif isprice(finalarray[3][finalarray[3].index(':') + 2:]) and float(finalarray[3][finalarray[3].index(':') + 2:]) < float(entry[l][entry[l].index(':') + 2:]):
                    finalarray[3] = entry[l]
            if "Date" in entry[l] and ':' in entry[l] and isitadate(entry[l][entry[l].index(':'):]) and foundDate == False:
                finalarray[1] = entry[l]
                foundDate = True
            if "Provider" in entry[l] and "N/A" not in entry[l] and foundprov == False:
                finalarray[2] = entry[l]
                foundprov = True
            if "payments and adjustments" in entry[l].lower() and foundadj == False:
                adjind = l
                foundadj = True
                if "N/A" not in entry[l] and ':' in entry[l] and isprice(entry[l][entry[l].index(':') + 2:]):
                    finalarray[4] = entry[l]
            if ':' not in entry[l] and '.' in entry[l].strip()[-4:] and isfloat(entry[l].strip()[-1:]):
                finalarray.append(entry[l])

with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt", 'w+') as f1:
    for line in finalarray:
        f1.write(line)

ddd = ''
numberss = ['1','2','3','4','5','6','7','8','9','0','/']
numbers = ['1','2','3','4','5','6','7','8','9','0']
#Replace the date in a format with which a directory can be made ('/' are replaced with '-')
with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt", "rb") as f1:
    lin = f1.readlines()
    with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + "temp.txt", 'w+') as f2:
        for l in lin:
            if 'Date:' in l:
                t = l
                for i in xrange(t.index(':') + 2, len(t)):
                    if t[i:i+1] not in numberss:
                        t=t.replace(t[i:i+1], '').strip()
                if t[-3] != "/":
                    t = t[0:t.rfind('/') + 1] + t[-2:]
                t = t.strip()
                for c in xrange(0, t.rfind('/')):
                    if t[c:c+1] == '0' and t[c+1:c+2] in numbers:
                        t = t[0:c] + t[c+1:]
                f2.write(t.replace('/', '-').strip())
                ddd = t.replace('/', '-').replace('Date: ', '').strip()
                f2.write("\n")
            else:
                f2.write(l)
os.rename(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + "temp.txt", sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt")

datspl = ddd.split('-')
tempdatspl = []
tempdatspl.append(datspl[2])
tempdatspl.append(datspl[0])
tempdatspl.append(datspl[1])
tempdatspl[0] = '20' + tempdatspl[0]
if len(tempdatspl[1]) == 1:
    tempdatspl[1] = '0' + tempdatspl[1]
if len(tempdatspl[2]) == 1:
    tempdatspl[2] = '0' + tempdatspl[2]

ddd = '-'.join(tempdatspl)

with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt", "rb") as f1:
    lin = f1.readlines()
    with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + "temp.txt", 'w+') as f2:
        for l in lin:
            if 'Date:' in l:
                f2.write("Date: " + ddd)
                f2.write('\n')
            else:
                f2.write(l)
os.rename(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + "temp.txt", sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt")




#Display results of process
with open(sys.argv[1][0:sys.argv[1].rfind('/') + 1] + prefix + "ServiceOutputFinal.txt", "rb") as f1:
    print("Service Information: \n")
    for lin in f1.readlines():
        print(lin.replace("\n",''))
    print("\n\nSee folder data/ to access data. Intermediate files are stored in subdirectory inter")

