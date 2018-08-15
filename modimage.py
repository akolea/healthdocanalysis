import cv2
import numpy as np
import plac
import argparse
import io
import os
import sys
import image1

img1 = image1.imageobj(sys.argv[1])

#img1.sharpen()
#os.rename("teemmpp.png", "123.png")

img1.contrast().sharpen()
os.rename("../output/teemmpp.png", "../output/9876.png")

#img1.contrasttoo()
#os.rename("teemmpp.png", "12345.png")

#img1.sharpen().contrast()
#os.rename("teemmpp.png", "123456.png")

#img1.sharpen().contrasttoo()
#os.rename("teemmpp.png", "1234567.png")
