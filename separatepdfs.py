from __future__ import unicode_literals, print_function
import csv
import extractjpg
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

from PyPDF2 import PdfFileWriter, PdfFileReader

#Load File
file_name = str(sys.argv[1])
inputpdf = PdfFileReader(open(file_name, "rb"), strict=False)

prefix = sys.argv[1][sys.argv[1].rfind('/') + 1:-4]
#Separate each page of the pdf
documents = []
for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    with open(file_name[0:file_name.rfind('/') + 1] + prefix + "doc%s.pdf" % i, "wb") as outputStream:
        output.write(outputStream)
        documents.append(file_name[0:file_name.rfind('/') + 1] + prefix + "doc%s.pdf" % i)


#Convert each page into an image
ee = extractjpg.extractor()

for i in xrange(0, len(documents)):
    print("Extracting page " + str(i+1))
    ee.extractImage(file_name[0:file_name.rfind('/') + 1], prefix, documents[i], i)


