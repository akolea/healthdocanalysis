#TEST EDIT#-------------------
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
import time
import pandas as pd
import json
import math
import fnmatch
import glob
import progressbar as pb
reload(sys)
sys.setdefaultencoding('utf8')
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from spacy.tokens import Span
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
from enum import Enum
from math import *
from time import sleep

for i in xrange(0,1):
    #Start progress bar
    widgets = ['PROGRESS: ', pb.Percentage(), ' ', pb.Bar('=', '[', ']'), ' ', pb.ETA()]
    timer = pb.ProgressBar(widgets=widgets, maxval=20).start()
    #Load Image
    image_file = str(sys.argv[1])
    im = Image.open(image_file)

    timer.update(1)
    time.sleep(0.1)

    client = vision.ImageAnnotatorClient()

    file_name = os.path.join(
        os.path.dirname(__file__),
        image_file)

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    #Do we already know the type of document or not?
    whatkind = ''
    try:
        whatkind = sys.argv[2]
    except IndexError:
        whatkind = ''

    newfile = '-n'
    newtxt = "w+"
    Servfile = ""
    EOBfile = ""

    argue = sys.argv[1][sys.argv[1].rfind('/') + 1:]
    if 'temp' in argue:
        Servfile = '../output/' + argue[0:-9] + "ServiceOutput" + str(len(glob.glob1('../output/', argue[0:-9] + "ServiceOutput*"))) + ".txt"
        EOBfile = '../output/' + argue[0:-9] + "EOBentries" + str(len(glob.glob1('../output/', argue[0:-9] + "EOBentries*"))) + ".csv"
    else:
        Servfile = '../output/' + argue[0:-4] + "ServiceOutput" + str(len(glob.glob1('../output/', argue[0:-4] + "ServiceOutput*"))) + ".txt"
        EOBfile = '../output/' + argue[0:-4] + "EOBentries" + str(len(glob.glob1('../output/', argue[0:-4] + "EOBentries*"))) + ".csv"


    #Load OCR
    response = client.text_detection(image=image)
    texts = response.text_annotations  #Raw data, all the words
    document = response.full_text_annotation
    textchars = []
    timer.update(2)
    timer.update(3)
    time.sleep(0.2)
    for page in document.pages:
            for block in page.blocks:
                block_words = []
                for paragraph in block.paragraphs:
                    block_words.extend(paragraph.words)
                block_symbols = []
                for word in block_words:
                    block_symbols.extend(word.symbols)
                block_text = ''
                for symbol in block_symbols:
                    block_text = block_text + symbol.text
                    textchars.append(symbol)
    textsdescrips = [] #String value of all the words
    for word in texts:
        if word.description.count('.') == 2:
            temp = word.description[0:word.description.index('.')+2] + "0"
            word.description = temp
    for word in texts:
         textsdescrips.append(word.description)


    #Some methods we need
    def isfloat(str):
        try:
            float(str.replace('$','').replace('-','').replace(',','').replace('S','').replace('(', '').replace(')',''))
            return True
        except ValueError:
            return False

    def isprice(str):
        if isfloat(str) and str.count(".") == 1 and isfloat(str[str.index('.') + 1:str.index('.') + 2]):
            return True
        else:
            return False

    def isitadate(str):
        if str.count("/") == 2 and len(str.strip()) < 15:
            return True
        else:
            return False

    timer.update(4)

    #Is the document an eob or bill?
    iseob = False
    isbill = False
    isother = False
    izdd = False
    izc = False
    whatkindofdocument = ""
    if whatkind == '-e':
        iseob = True
        isbill = False
        isother = False
        whatkindofdocument = "DOCUMENT TYPE: EOB"
    elif whatkind == '-b':
        isbill = True
        iseob = False
        isother = False
        whatkindofdocument = "DOCUMENT TYPE: EOB"
    elif whatkind == '-o':
        isbill = False
        iseob = False
        isother = True
        whatkindofdocument = "DOCUMENT TYPE: OTHER"
    else:
        for page in document.pages:
            for block in page.blocks:
                block_words = []
                for paragraph in block.paragraphs:
                    block_words.extend(paragraph.words)

                block_symbols = []
                for word in block_words:
                    block_symbols.extend(word.symbols)
                block_text = ''
                for symbol in block_symbols:
                    block_text = block_text + symbol.text
                    if block_text.lower() == 'explanationofbenefits' or 'explanation' in block_text.lower():
                        iseob = True
                        whatkindofdocument = "DOCUMENT TYPE: EOB"
        timer.update(6)
        timer.update(7)
        if iseob == False:
            for tt in texts:
                if tt.description.lower() == "eob":
                    iseob = True
                    whatkindofdocument = "DOCUMENT TYPE: EOB"
        if iseob == False:
            for tt in texts:
                if tt.description.lower().strip() == "deductible":
                    izdd = True
                if tt.description.lower().replace("-", '').strip() == "coinsurance" or tt.description.lower().replace("-", '').strip() == "copay":
                    izc = True
            if izc and izdd:
                iseob = True
                whatkindofdocument = "DOCUMENT TYPE: EOB"
        timer.update(8)
        for page in document.pages:
            for block in page.blocks:
                block_words = []
                for paragraph in block.paragraphs:
                    block_words.extend(paragraph.words)
                block_symbols = []
                for word in block_words:
                    block_symbols.extend(word.symbols)
                block_text = ''
                for symbol in block_symbols:
                    block_text = block_text + symbol.text
                    if block_text.lower() == 'thisisnotabill' and iseob == False:
                        isother = True
                        whatkindofdocument = "DOCUMENT TYPE: OTHER"
        if isother == False and iseob == False:
            isbill = True
            whatkindofdocument = "DOCUMENT TYPE: BILL"
    timer.update(9)
    #---------------CREATE CHARACTER BY CHARACTER ARRAY-----------------------
    timer.update(10)
    time.sleep(0.1)

    canchar = False #Can we even do a character by character analysis?
    textsdescripschar = [] #String value of all the characters

    for word in textchars:
         textsdescripschar.append(word.text)
    heightschar = []
    divideit = 0

    for i in xrange(1, len(textchars)-1):
        if textchars[i].bounding_box.vertices[2].y != textchars[i].bounding_box.vertices[1].y:
            heightofonechar = im.height / (textchars[i].bounding_box.vertices[3].y - textchars[i].bounding_box.vertices[1].y)
            heightschar.append(heightofonechar)
            divideit += 1
    heightschar = sorted(heightschar)
    heightmchar = heightschar[len(heightschar) / 2]  #medium height of characters

    widthschar = []
    for i in xrange(1, len(textchars)-1):
        if textchars[i].bounding_box.vertices[1].x != textchars[i].bounding_box.vertices[0].x:
            widthofonechar = im.width / (textchars[i].bounding_box.vertices[1].x - textchars[i].bounding_box.vertices[0].x)
            widthschar.append(widthofonechar)
    widthschar = sorted(widthschar)
    widthmchar = widthschar[len(widthschar)/2]  #medium width of characters


    #Are the characters big enough to do piece together
    if len(widthschar) > 7 and widthmchar > 0 and widthmchar < im.width and len(heightschar) > 7 and heightmchar > 0 and heightmchar < im.height:
        canchar = True

    if canchar:
        #We make normalized arrays, where arrchar is reading updown, and arrflipchar is reading left to right
        arrchar = [['' for i in xrange(heightmchar)] for i in xrange(widthmchar)]

        for i in xrange(1, len(textchars)):
            arrchar[(((textchars[i].bounding_box.vertices[0].x + textchars[i].bounding_box.vertices[1].x) / 2) * widthmchar)/im.width][(((textchars[i].bounding_box.vertices[3].y + textchars[i].bounding_box.vertices[0].y) / 2) * heightmchar)/im.height] = str(textchars[i].text)

        arrcopychar = arrchar
        arrflipchar = zip(*arrchar)
        arrflipchar[:] = [list(t) for t in arrflipchar]
        arrflipcopychar = arrflipchar

        arrflipcopychar = [x for x in arrflipcopychar if x!= ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
        arrflipcop1 = [[x or ' ' for x in sublist] for sublist in arrflipcopychar]
        arrflipcopychar = arrflipcop1

        for m in xrange(0, len(arrflipcopychar)):
            if arrflipcopychar[m].count('.') > 2:
                templist = [x for x in arrflipcopychar[m] if x!=' ']
                if templist[2] == '/' or templist[1] == '/':
                    for i in xrange(0, len(arrflipcopychar[m]) - 4):
                        if arrflipcopychar[m][i] != ' ' and arrflipcopychar[m][i] != '|'  and arrflipcopychar[m][i+1] == ' '  and arrflipcopychar[m][i+2] == ' ' and arrflipcopychar[m][i+ 3] == ' ':
                            lastint = 0
                            numspace = 0
                            for g in xrange(i+1, len(arrflipcopychar[m])):
                                if arrflipcopychar[m][g] != ' ' and arrflipcopychar[m][g] != '|':
                                    lastint = g
                                    break
                            numspace = arrflipcopychar[m][i+1:lastint].count(' ')
                            if numspace % 2 == 0:
                                arrflipcopychar[m].insert(i+(numspace/2), '|')
                            else:
                                arrflipcopychar[m].insert(i+(numspace/2), '|')
        timer.update(11)
        for m in xrange(0, len(arrflipcopychar)):
            if arrflipcopychar[m].count('.') > 2:
                templist = [x for x in arrflipcopychar[m] if x!=' ']
                if templist[2] == '/' or templist[1] == '/':
                    for i in xrange(0, len(arrflipcopychar[m]) - 3):
                        if arrflipcopychar[m][i] == ' ' and arrflipcopychar[m][i+1] != ' ' and arrflipcopychar[m][i-1] != ' ' and arrflipcopychar[m][i+1] != '|' and arrflipcopychar[m][i-1] != '|':
                            arrflipcopychar[m][i] = ''
                            arrflipcopychar[m].insert(arrflipcopychar[m][i:-1].index('|')  - 1, '')
        #Piecing together full document
        fulldoc=[]
        for i in xrange(0, len(arrflipcopychar)):
            tempsent11 = ""
            for a in arrflipcopychar[i]:
                tempsent11 += a
            fulldoc.append(tempsent11)

        sssenttt=[]
        for i in xrange(0, len(arrflipcopychar)):
    #    templist1 = [x for x in arrflipcopychar[i] if x!=' ']
    #    if templist1[2] == '/' or templist1[1] == '/':
            if arrflipcopychar[i].count('.') > 2 and arrflipcopychar[i].count('|') > 3:
                tempsent1 = ""
                for a in arrflipcopychar[i]:
                    tempsent1 += a
                sssenttt.append(tempsent1)

        timer.update(15)
    #Remove empty values
        for liset in arrflipchar:
            liset[:] = [item for item in liset if item != '']
        for liset in arrcopychar:
            liset[:] = [item for item in liset if item != '']

        time.sleep(0.5)

    #Create sentences from the document
        numberssz = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        HORIZONTALSENTENCESCHAR = []
        for i in xrange(0, len(arrflipchar)-1):
            sentence = ""
            for n in xrange(0, len(arrflipchar[i])):
                if arrflipchar[i][n].count("/") == 2 and arrflipchar[i][n][0:1] in numberssz:  # find the items with a date, probably refer to service
                    sentence += "#*! "
                sentence += arrflipchar[i][n]
                sentence += " "
            HORIZONTALSENTENCESCHAR.append(sentence)

    #Remove the empty lists
        HORIZONTALSENTENCESCHAR[:] = [item for item in HORIZONTALSENTENCESCHAR if item != '']


    #Read Top to Bottom using the following method, left and right vertices are extended downwoard and any words that fall within are part of the reading up and down
        UPDOWNCHAR = []
        usedindexchar = []
        for n in xrange(0, len(textchars)):
            if n not in usedindexchar:
                usedindexchar.append(n)
                tomakechar = []
                tomakechar.append(textchars[n].text)
                for j in xrange(n+1, len(textchars)):
                    if ((textchars[n].bounding_box.vertices[1].x < textchars[j].bounding_box.vertices[1].x and textchars[n].bounding_box.vertices[1].x > textchars[j].bounding_box.vertices[0].x) or (textchars[n].bounding_box.vertices[0].x < textchars[j].bounding_box.vertices[1].x and textchars[n].bounding_box.vertices[0].x > textchars[j].bounding_box.vertices[0].x) or ((textchars[n].bounding_box.vertices[0].x + textchars[n].bounding_box.vertices[1].x) / 2 < textchars[j].bounding_box.vertices[1].x and (textchars[n].bounding_box.vertices[0].x + textchars[n].bounding_box.vertices[1].x) / 2 > textchars[j].bounding_box.vertices[0].x)) and (textchars[n].bounding_box.vertices[1].y - textchars[j].bounding_box.vertices[2].y < heightmchar):
                        if('.' in textchars[textsdescripschar.index(tomakechar[-1])].text and '.' not in textchars[j].text):
                            break
                        else:
                            tomakechar.append(textchars[j].text)
                UPDOWNCHAR.append(tomakechar)


        for listaA in UPDOWNCHAR:
            for wordaA in listaA:
                wordaA.replace(',','')
    #---------------------------CHARACTERBYCHARACTEREXTRACTION-----------------------------------#
    timer.update(16)



    #Determine the dimensions of individual textboxes
    heights = []
    for i in xrange(1, len(texts)):
        heightofone = im.height / (texts[i].bounding_poly.vertices[2].y - texts[i].bounding_poly.vertices[1].y)
        heights.append(heightofone)

    heights = sorted(heights)
    heightm = heights[len(heights) / 2] #medium height of a word

    widths = []
    for i in xrange(1, len(texts)):
        widthofone = im.width / (texts[i].bounding_poly.vertices[1].x - texts[i].bounding_poly.vertices[0].x)
        widths.append(widthofone)

    widths = sorted(widths)
    widthm = widths[len(widths)/2] #medium width of a word

    #arr is the normalized grid reading up and down, arrflip is left to right
    arr = [['' for i in xrange(heightm)] for i in xrange(widthm)]

    for i in xrange(1, len(texts)):
        arr[(((texts[i].bounding_poly.vertices[0].x + texts[i].bounding_poly.vertices[1].x) / 2)*widthm) / im.width][(((texts[i].bounding_poly.vertices[3].y + texts[i].bounding_poly.vertices[0].y) / 2) * heightm) / im.height] = str(texts[i].description)

    arrcopy = arr

    arrflip = zip(*arr)

    arrflip[:] = [list(t) for t in arrflip]


    arrflipcopy = arrflip
    #arrflipcopy = [x for x in arrflipcopy if x != ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
    arrflipcop2 = [[x or ' ' for x in sublist] for sublist in arrflipcopy]
    arrflipcopy = arrflipcop2

    timer.update(17)
    timer.update(18)
    sssenttt2=[]
    for i in xrange(0, len(arrcopy)-1):
        tempsent2 = " "
        for n in xrange(0, len(arrcopy[i])):
            tempsent2 += arrcopy[i][n]
        sssenttt2.append(tempsent2)
    #Remove empty values
    for liset in arrflip:
        liset[:] = [item for item in liset if item != '']
    for liset in arrcopy:
        liset[:] = [item for item in liset if item != '']


    #Create sentences from the document using the left to right array
    numberss = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    datebounds = []
    alldates = []
    linedates = []
    HORIZONTALSENTENCES = []
    for i in xrange(0, len(arrflip)-1):
        sentence = ""
        for n in xrange(0, len(arrflip[i])):
            if arrflip[i][n].count("/") == 2 and arrflip[i][n][0:1] in numberss and len(arrflip[i]) > 3 and '.' in arrflip[i][-2]:  # find the items with a date, probably refer to service
                sentence += "#*! "
                linedates.append(arrflip[i][n].replace("-", ''))
            sentence += arrflip[i][n]
            sentence += " "
        HORIZONTALSENTENCES.append(sentence)

    for tt in texts:
        if isitadate(tt.description):
            alldates.append(tt.description)

    lettersnumbers = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m','1','2','3','4','5','6','7','8','9','0']

    #This approach uses an appraoch where the top and bottom vertices horizontal lines are extended and then all words that fall within the bounds form sentence
    HORIZONTALS = []
    timer.update(18)
    time.sleep(0.5)
    timer.update(19)
    usedindex2 =[]
    for n in xrange(0, len(texts)):
        if n not in usedindex2:
            usedindex2.append(n)
            tomake2 = []
            tomake2.append(texts[n].description)
            for j in xrange(n+1, len(texts)):
                if (texts[n].bounding_poly.vertices[2].y + (widthm) > texts[j].bounding_poly.vertices[2].y) and (texts[n].bounding_poly.vertices[1].y - (widthm) < texts[j].bounding_poly.vertices[1].y):
                    tomake2.append(texts[j].description)
            HORIZONTALS.append(tomake2)

    #Remove the empty lists
    HORIZONTALSENTENCES[:] = [item for item in HORIZONTALSENTENCES if item != '']
    HORIZONTALS[:] = [item for item in HORIZONTALS if item != '']
    #End progress on creation of sentences
    timer.update(20)
    timer.finish()
    time.sleep(1)
    print("\n\n\n")
    print("SENTENCES CONTAINED WITHIN FILE: ")
    for a in HORIZONTALSENTENCES:
        print(a)
    print("\n\n\n\n")

    with open(Servfile.replace('ServiceOutput', 'OCRSentences'), 'w+') as f1:
        f1.write("SENTENCES CONTAINED WITHIN FILE: ")
        for s in HORIZONTALSENTENCES:
            f1.write(s)

    #Read Top to Bottom using the following method, left and right vertices are extended downwoard and any words that fall within are part of the reading up and down
    UPDOWN = []
    usedindex = []
    for n in xrange(0, len(texts)):
        if n not in usedindex:
            usedindex.append(n)
            tomake = []
            tomake.append(texts[n].description)
            for j in xrange(n+1, len(texts)):
                if ((texts[n].bounding_poly.vertices[1].x < texts[j].bounding_poly.vertices[1].x and texts[n].bounding_poly.vertices[1].x > texts[j].bounding_poly.vertices[0].x) or (texts[n].bounding_poly.vertices[0].x < texts[j].bounding_poly.vertices[1].x and texts[n].bounding_poly.vertices[0].x > texts[j].bounding_poly.vertices[0].x) or ((texts[n].bounding_poly.vertices[0].x + texts[n].bounding_poly.vertices[1].x) / 2 < texts[j].bounding_poly.vertices[1].x and (texts[n].bounding_poly.vertices[0].x + texts[n].bounding_poly.vertices[1].x) / 2 > texts[j].bounding_poly.vertices[0].x)) and texts[n].bounding_poly.vertices[1].y-texts[j].bounding_poly.vertices[2].y < heightm:
                    if('.' in texts[textsdescrips.index(tomake[-1])].description and '.' not in texts[j].description):
                        break
                    else:
                        tomake.append(texts[j].description)
            UPDOWN.append(tomake)

    for lista in UPDOWN:
        for worda in lista:
            worda.replace(',','')

    servicelines123 = []
    for lineI in HORIZONTALSENTENCES:
        if lineI[0:3] == "#*!":
            servicelines123.append(lineI)

    datels = []
    descripls = []
    coils = []
    copls = []
    ddls = []
    totls = []
    youowels = []

    #Key Values we might want to know
    ddamount = 123456789.00
    coiamount = 123456789.00
    copamount = 123456789.00
    billtotal = 123456789.00
    paymentsadj = 123456789.00
    notcovered = 123456789.00
    youowee = 123456789.00
    toreplace = False
    linetoreplace = ""
    firstdate = ""

    #Rewrite file for total amount
    def replace(file_path, pattern, subst):
        fh, abs_path = mkstemp()
        with fdopen(fh,'w') as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    new_file.write(line.replace(pattern, subst))
        remove(file_path)
        move(abs_path, file_path)

    #Finds a target value in two dimensional array
    def findinarr(target):
        for i,lst in enumerate(arrcopy):
            for j,thing in enumerate(lst):
                if thing == target:
                    return (i, j)
        return (None, None)
    #Get the indices of the date boxes, as well as their positions
    indiiix = [0]
    for see in HORIZONTALSENTENCES:
        if "#*!" == see[0:3]:
            temp = see.split(" ")
            for word in temp:
                if isitadate(word) == True:
                    for w in xrange(indiiix[-1], len(texts)):
                        if texts[w].description == word:
                            tt= []
                            tt.append(texts[w].bounding_poly.vertices[0].y)
                            tt.append(texts[w].bounding_poly.vertices[3].y)
                            datebounds.append(tt)
                            indiiix.append(w)

    wordsfoundintable = ["-","-","-"] #will need when creating template

    #Find the date of service by finding the least recent date. In EOB, we only consider the dates in service lines. For bill, we consider all dates on page
    datesplited = []
    if iseob:
        for dd in linedates:
            datesplited.append(dd.split("/"))
    if isbill:
        for dd in alldates:
            datesplited.append(dd.split("/"))
    for j in xrange(0, len(datesplited)):
        for k in xrange(0, len(datesplited[j])):
            datesplited[j][k] = datesplited[j][k].replace('$','').replace('-','').replace(',','').replace('S','')

    for fff in datesplited:
        if isfloat(fff[2][-2:]):
            lowestentry = float(fff[2][-2:])
            break
    lowvalue = 1000

    #First test year, then month, then day
    for j in xrange(0, len(datesplited)):
        if isfloat(datesplited[j][2][-2:]) and float(datesplited[j][2][-2:]) < lowestentry:
            lowvalue = j
            lowestentry = float(datesplited[j][2][-2:])
    if lowvalue == 1000:
        for j in xrange(0, len(datesplited)):
            if isfloat(datesplited[j][0]) and float(datesplited[j][0]) < lowestentry:
                lowvalue = j
                lowestentry = float(datesplited[j][0])
    if lowvalue == 1000:
        for j in xrange(0, len(datesplited)):
            if isfloat(datesplited[j][1]) and float(datesplited[j][1]) < lowestentry:
                lowvalue = j
                lowestentry = float(datesplited[j][1])
    if lowvalue == 1000:
        lowvalue = 0

    if len(alldates) > lowvalue:
        firstdate = alldates[lowvalue]

    istheretable = False


    #If the document is an eob, try finding the deductivle, coinsurrance, copay. Then for every entry, replicate it. the largest numerical entry is the toal charge 
    #and the right most entry is the money the patient owes For deductible, coinsurance and copay we are using the UPDOWN array to try and find columns which contain
    #each word and associated dollar values.
    if iseob == True:
        sentencestoadd = []
        sentencestoaddcopy = []
        for listerr in UPDOWN:
            if listerr[0].lower() == "deductible":
                wordsfoundintable[0] = listerr[0]
                for word in listerr:
                    if '.' in word and isfloat(word):
                        if '$' in word:
                            word = word.replace('$', '')
                        if 'S' in word:
                            word = word.replace('S', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if '-' in word:
                            word = word.replace('-', '')
                        ddamount = float(word.strip())
            if listerr[0].lower() == "coinsurance" or listerr[0].lower() == "co-insurance" or (listerr[0].lower() == "co" and listerr[1].lower() == "insurance"):
                if listerr[0].lower() != "co":
                    wordsfoundintable[2] = listerr[0].replace("-",'').replace("S", '')
                else:
                    wordsfoundintable[2] = listerr[1].replace("-",'').replace("S", '')
                for word in listerr:
                    if '.' in word and isfloat(word):
                        if '$' in word:
                            word = word.replace('$', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if '-' in word:
                            word = word.replace('-', '')
                        if 'S' in word:
                            word = word.replace('S', '')
                        coiamount = float(word.strip())
            if listerr[0].lower() == "copay" or listerr[0].lower() == "co-pay" or (listerr[0].lower() == "co" and listerr[1].lower() == "pay"):
                if listerr[0].lower() != "co":
                    wordsfoundintable[1] = listerr[0].replace("-",'').replace("S", '')
                else:
                    wordsfoundintable[1] = listerr[1].replace("-",'').replace("S", '')
                for word in listerr:
                    if '.' in word and isfloat(word):
                        if '$' in word:
                            word = word.replace('$', '')
                        if ',' in word:
                            word = word.replace(',', '')
                        if '-' in word:
                            word = word.replace('-', '')
                        if 'S' in word:
                            word = word.replace('S', '')
                        copamount = float(word.strip())
        with open(Servfile, newtxt) as text_file:
            totalsentry = []
            youowes = []
            for esentence in HORIZONTALSENTENCES:
                if esentence[0:3] == "#*!" and len(esentence.split()) > 2:
                    sentencestoaddcopy.append(esentence)
                    esentence = esentence.replace('$', '')
                    esentence = esentence.replace('S', '')
                    esentence = esentence.replace('-', '')
                    esentence = esentence.replace(',', '')
                    sentencestoadd.append(esentence)
                    templist = esentence.split()
                    costs = []
                    for word in templist:
                        if '.' in word and any(ext in word for ext in numberss):
                            if '$' in word:
                                word = word.replace('$', '')
                            if ',' in word:
                                word = word.replace(',', '')
                            if '-' in word:
                                word = word.replace('-', '')
                            if 'S' in word:
                                word = word.replace('S', '')
                            costs.append(float(word[0:word.index('.') + 2] + "0"))
                    if len(costs)>1:
                        totalsentry.append(max(costs))
                        youowes.append(costs[-1])
            totls = totalsentry
            if len(totalsentry) > 0:
                billtotal = sum(totalsentry)
            if len(youowes) > 0:
                youowee = sum(youowes)
            for line in text_file:
                if "Total" in line and newfile != '-n':
                    toreplace = True
                    linetoreplace = line
            if toreplace == False:
                if billtotal != 123456789.00:
                    text_file.write("\n" + "Total: {0}".format(billtotal))
                    text_file.write("\n")
                else:
                    text_file.write("Total: N/A")
                    text_file.write("\n")
            if isitadate(firstdate):
                text_file.write("Date: " + firstdate)
                text_file.write("\n")
            else:
                text_file.write("Date: N/A")
                text_file.write("\n")
            if youowee != 123456789.00:
                text_file.write("You Owe: {0}".format(youowee))
                text_file.write("\n")
            else:
                text_file.write("You Owe: N/A")
                text_file.write("\n")
            if ddamount != 123456789.00:
                text_file.write("Deductible: {0}".format(ddamount))
                text_file.write("\n")
            else:
                text_file.write("Deductible: N/A")
                text_file.write("\n")
            if coiamount != 123456789.00:
                text_file.write("Coinsurance: {0}".format(coiamount))
                text_file.write("\n")
            else:
                text_file.write("Coinsurance: N/A")
                text_file.write("\n")
            if copamount != 123456789.00:
                text_file.write("Copay: {0}".format(copamount))
                text_file.write("\n")
            else:
                text_file.write("Copay: N/A")
                text_file.write("\n")
            for w in xrange(0, len(sentencestoaddcopy)):
                temp = (sentencestoaddcopy[w].replace("S", '').replace("$", '').replace(',', '').replace('-','')).split(" ")
                temp = temp[1:len(temp)]
                for i in xrange(0, len(temp) - 1):
                    if isitadate(temp[i]) or isprice(temp[i]):
                        if i != 0 and "\t" not in temp[i-1]:
                            temp[i] = "\t" + temp[i] + "\t"
                        else:
                            temp[i] = temp[i] + "\t"
                for i in xrange(1, len(temp) - 1):
                    if "\t" not in temp[i+1]:
                        temp[i] = temp[i] + " "
                sentencestoaddcopy[w] = ''.join(temp)
                anothersentencetoadd = ""
        if toreplace == True:
            replace(Servfile, linetoreplace, "Total Charges: {0}".format(billtotal)+"\n")


        #If we want to build a dataframe, we have the rows in service lines. However, we must find the headers for each column
        headers = []
        sentencestoaddcopy2 = sentencestoaddcopy
        for i in xrange(0, len(sentencestoaddcopy2)):
            sentencestoaddcopy2[i] = sentencestoaddcopy2[i][0:len(sentencestoaddcopy[i])].replace("\t", '|').replace("$", '').replace("S", '').replace(",",'')

        newlineaddme = ''

        with open(EOBfile, "w+") as text_file:
            for sentencestoaddz in sentencestoaddcopy:
                text_file.write((sentencestoaddz[0:len(sentencestoaddz)].replace("\t", '|').replace("$", '').replace("S", '').replace(",",'')))
                text_file.write("\n")
        with open(EOBfile, 'rb') as text_file:
            if len(text_file.readlines()) > 0:
                istheretable = True

        if istheretable:
            with open(EOBfile, 'rb') as text_file:
                redlin = text_file.readlines()
                temp = redlin[0].replace(" \n",'').replace(" ", '').replace("\n", '').split("|")
                for q in xrange(0, len(temp)):
                    if temp[q] != '':
    	                headers.append('-')

            #This poriton deals with an offset of rows and columns, ie if one entry in the table is left blank, we must avoid offsetting the whole datafram
            with open(EOBfile, "r+") as texto_file:
                redlin = []
                redlin = texto_file.readlines()
                if len(redlin) > 1:
                    for r in xrange(0, len(redlin) - 1):
                        if redlin[r].count('|') > redlin[r+1].count('|'):
                            whichcol = 1
                            for x in xrange(0, len(sssenttt[r])-5):
                                startind=0
                                finind = 0
                                f=r
                                if sssenttt[f][x:x+1] == '|' and '|' in sssenttt[f][x+1:]:
                                    startind = x
                                    finind = (sssenttt[r][x+1:]).index('|') + x
                                    if any(ext in sssenttt[r+1][startind:finind].split() for ext in lettersnumbers) == False and whichcol != 1:
                                        tempiii = []
                                        tempiii = redlin[r+1].split("|")
                                        tempiii.insert(whichcol, '-')
                                        redlin[r+1] = "|".join(tempiii)
    				        headers.append('-')
    				        break
                                        break
                                    whichcol = whichcol + 1
                                    x = finind + 1
                                else:
                                    x = x+1
                        elif redlin[r].count('|') < redlin[r+1].count('|'):
                            whichcol = 1
                            for x in xrange(0, len(sssenttt[r+1])-5):
                                startind=0
                                finind = 0
                                f=r
                                if sssenttt[f+1][x:x+1] == '|' and '|' in sssenttt[f+1][x+1:]:
                                    startind = x
                                    finind = (sssenttt[r+1][x+1:]).index('|') + x
                                    if any(ext in sssenttt[r][startind:finind].split() for ext in lettersnumbers) == False and whichcol != 1:
                                        tempiii = []
                                        tempiii = redlin[r].split("|")
                                        tempiii.insert(whichcol, '-')
                                        redlin[r] = "|".join(tempiii)
        			        headers.append('-')
    				        break
                                        break
                                    whichcol = whichcol + 1
                                    x = finind + 1
                                else:
                                    x = x+1
                with open("nebie.txt", "w+") as t2:
                    for lineaa in redlin:
                        t2.write(lineaa)
            os.rename("nebie.txt", EOBfile)

            #Actually creating the table
            with open(EOBfile, "r+") as text_file:
                headers[0] = "Date"
                total = 0
                totind = 0
                descripind = 0
                ivefoundit = False
                ddind = 123123
                copind = 123123
                coiind = 123123
                foundthed = False
                revusedindices = []
                usedindices = []
                sentencestoaddcopy22 = text_file.readlines()
                for g in xrange(0, len(sentencestoaddcopy22[0].split('|'))):
                    word = sentencestoaddcopy22[0].split('|')[g]
                    tempdd = 0
                    tempcpy = 0
                    tempcoi = 0
                    if isfloat(word) and float(word) > total:
                        total = float(word)
                        totind = g
                    if isfloat(word) == False and ivefoundit == False and g != 0:
                        descripind = g
                        ivefoundit = True
                    for l in xrange(0, len(sentencestoaddcopy22)):
                        if isfloat(sentencestoaddcopy22[l].split('|')[g]):
                            tempdd += float(sentencestoaddcopy22[l].split('|')[g])
                            tempcpy += float(sentencestoaddcopy22[l].split('|')[g])
                            tempcoi += float(sentencestoaddcopy22[l].split('|')[g])
                    if foundthed == False:
                        if ddamount != 0 and tempdd == ddamount:
                            ddind = g
    		            if copamount != 123456789.00:
                                copind = g+1
                            if coiamount != 123456789.00:
    			        coiind = g+2
                            foundthed = True
                        elif copamount != 0 and tempcpy == copamount:
    		            if ddamount != 123456789.00:
                                ddind = g-1
                            copind = g
                            if coiamount != 123456789.00:
    			        coiind = g+1
                            foundthed = True
                        elif coiamount != 0 and tempcoi == coiamount:
                            if ddamount != 123456789.00:
    			        ddind = g-2
                            if copamount != 123456789.00:
    		    	        copind = g-1
                            coiind = g
                            foundthed = True
                if ddind != 123123:
    	            usedindices.append(ddind)
                if copind != 123123:
                    usedindices.append(copind)
                if coiind != 123123:
                    usedindices.append(coiind)
                usedindices.append(1)
    	        usedindices.append(0)
                usedindices.append(descripind)
                usedpriorwords = []
                parserow = 0
                numoflinee = 0
                headers[totind] = "Total Charges"
                if ddind != 123123:
    	            headers[ddind] = "Deductible"
                if copind != 123123:
    	            headers[copind] = "Co-Pay"
                if coiind != 123123:
    	            headers[coiind] = "Co-Insurance"
                headers[1] = "Service"
                headers[-1] = "Amount You Owe"
                newlineaddme = '|'.join(headers)

            info = []
            with open(EOBfile, "rb") as t3:
                redlin = t3.readlines()
                for l in redlin:
                    info.append(l.split('|'))
            for j in xrange(0, len(info)):
                info[j] = info[j][0:-1]
            df = pd.DataFrame(info, index = None, columns = headers) #, na_values=[' - '])

            with open("newiefile.txt", 'w+') as f1:
                with open(Servfile, 'rb') as f2:
                    for line in f2.readlines():
                        f1.write(line)
                    f1.write(df.to_string())
            os.rename("newiefile.txt", Servfile)

        with open("nu.txt", 'w+') as f1:
            with open(Servfile, 'rb') as f2:
                f1.write("Document Type: EOB")
                f1.write("\n")
                for lin in f2.readlines():
                    f1.write(lin)
        os.rename("nu.txt", Servfile)
#----------------THE FOLLOWING IS ANALYZING BILLS------------------#

    badwords = ['payment', 'payments', 'adjustment', 'adjustments', 'PAYMENTS', 'Payments', 'PAYMENT', 'Payment', 'ADJUSTMENTS', 'Adjustments', 'ADJUSTMENT', 'Adjustment', 'PAYMENTS/ADJUSTMENTS', 'payments/adjustments']
    gtfo = False
    isthereatotal = False
    PROVIDERLINE = ""
    #Determine Bill Provider using NLP tools, as well as heuristics
    if isbill:
        providers = []
        actualprovider = []
        nlp = spacy.load('./en_example_model/en_provider-2.0.0/en_provider/en_provider-2.0.0')
        for ss in HORIZONTALSENTENCES:
            docz = nlp(ss)
            for ent in docz.ents:
                if ent.label_ == 'PROVIDER':
                    providers.append(ent.text)
        if len(providers) > 1:
            for prov in providers:
                if 'hospital' in prov.lower() or 'center' in prov.lower() or 'medical' in prov.lower() or 'clinic' in prov.lower() or 'dent' in prov.lower() or 'orth' in prov.lower() or 'phys' in prov.lower() or 'presby' in prov.lower() or 'valley' in prov.lower() or 'gastro' in prov.lower() or 'resp' in prov.lower():
                    actualprovider.append(prov)
        else:
            actualprovider.append(providers[0])
        if len(actualprovider) > 0:
            PROVIDERLINE = "Provider: " + actualprovider[0]
        else:
            PROVIDERLINE = "Provider: N/A"

    #Find the total value from a bill
    if isbill == True:
        TOTALV = []
        for l in texts:
            if isprice(l.description.replace('$', '').replace('S', '').replace('-', '').replace(',','')):
                TOTALV.append(float(l.description.replace('$', '').replace('S', '').replace('-', '').replace(',','').replace('(','').replace(')','')))
        if len(TOTALV) > 0:
            billtotal = max(TOTALV)
            istherealtotal = True

    #Find the payments and adjustments from a bill
    goo = False
    if isbill == True:
        for listt in HORIZONTALSENTENCES:
            if 'payment' in listt.lower() and 'adjustment' in listt.lower():
                for word in listt.split(" "):
                    if isprice(word) and float(word.replace('$', '').replace('S', '').replace('-', '').replace(',','').replace('(','').replace(')','').strip()) < billtotal:
                        if paymentsadj == 123456789.00:
                            paymentsadj = 0.00
                        paymentsadj = float(word.replace('$', '').replace('S', '').replace('-', '').replace(',','').replace('(','').replace(')','').strip())
                        goo = True
        if goo == False:
            for listt in HORIZONTALSENTENCES:
                if 'payment' in listt.lower() or 'adjustment' in listt.lower():
                    for word in listt.split(" "):
                        if isprice(word) and float(word.replace('$', '').replace('S', '').replace('-', '').replace(',','').replace('(','').replace(')','').strip()) < billtotal:
                            if paymentsadj == 123456789.00:
                                paymentsadj = 0.00
                            paymentsadj += float(word.replace('$', '').replace('S', '').replace('-', '').replace(',','').replace('(','').replace(')','').strip())

    #Write the bill to ServiceOutput
    records1 = []
    if isbill == True:
        for ss in HORIZONTALSENTENCES:
            if len(ss.strip().split(" ")) > 1 and (isprice(ss.strip().split(" ")[-1]) or isprice(ss.strip().split(" ")[-2])):
                records1.append(ss)
    if isbill == True:
        with open(Servfile, newtxt) as text_file:
            for line in text_file:
                if "Total" in line and newfile != '-n':
                    toreplace = True
                    linetoreplace = line
            text_file.write("Document Type: Bill")
            text_file.write("\n")
            text_file.write(PROVIDERLINE)
            text_file.write("\n")
            text_file.write("Date: " + firstdate)
            if billtotal != 123456789.00:
                text_file.write("\n" + "Total: {0}".format(billtotal))
                text_file.write("\n")
            else:
                text_file.write("Total: N/A")
                text_file.write("\n")
            if paymentsadj != 123456789.00:
                text_file.write("Payments and Adjustments: {0}".format(paymentsadj))
                text_file.write("\n")
            else:
                text_file.write("Payments and adjustments: N/A")
                text_file.write("\n")
            if len(records1) > 0:
                text_file.write("\n\n")
                for r in records1:
                    if 'total' not in r.lower() and 'payment' not in r.lower() and 'adjust' not in r.lower() and 'owe' not in r.lower() and 'balance' not in r.lower() and 'discount' not in r.lower() and 'insurance' not in r.lower():
                        text_file.write(r + "\n")

    #Store the type of document
    with open("../output/whatkind.txt", 'w+') as f1:
        f1.write(whatkindofdocument)

    #Write the NLP text files
    if iseob:
        with open("../output/NLPSERVICELINES.txt", 'a') as f1:
            for sent in HORIZONTALSENTENCES:
                if "#*!" in sent:
                    f1.write(sent.replace("#*!", '').strip())
                    f1.write("\n")
    with open("../output/NLPHORIZONTALS.txt", 'a') as f2:
        for s in xrange(2, len(HORIZONTALSENTENCES)):
            if "#*!" in HORIZONTALSENTENCES[s]:
                f2.write(HORIZONTALSENTENCES[s].replace("#*!", '').strip())
                f2.write("\n")
            else:
                f2.write(HORIZONTALSENTENCES[s])
                f2.write("\n")

