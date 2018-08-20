import cv2
import numpy as np
import argparse

from PIL import Image, ImageDraw, ImageFont
from numpy import array
class imageobj:
    image = ""
    def __init__(self, img):
        self.image = img

    def selfreturn(self):
        return self.image

    def convtoim(self, arr):
        img = Image.fromarray(arr)
        out = ''
        with open("dirname.txt", rb) as f1:
            out = f1.readlines()[0]
        img.save(out + "teemmpp.png")
        outstriing = out + "teemmpp.png"
        return outstriing
    #Rotate the image to make it horizontal
    def rotate(self):
        iii = cv2.imread(self.image)
        gray = cv2.cvtColor(iii, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)

        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)

        else:
            angle = angle

        (h, w) = iii.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(iii, M, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        final = imageobj(self.convtoim(rotated))
        return final

    #Apply a filter which sharpens the image
    def sharpen(self):
        iii = cv2.imread(self.image)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(iii, -1, kernel)

        final = imageobj(self.convtoim(sharpened))
        return final
    #Apply filter which increases contrast of image
    def contrast(self):
        iii = cv2.imread(self.image)
        imghsv = cv2.cvtColor(iii, cv2.COLOR_BGR2HSV)

        imghsv[:, :, 2] = [[max(pixel - 5, 0) if pixel < 190 else min(pixel + 5, 255) for pixel in row] for row in
                           imghsv[:, :, 2]]
        contrasted = cv2.cvtColor(imghsv, cv2.COLOR_HSV2BGR)

        final = imageobj(self.convtoim(contrasted))
        return final
    def contrasttoo(self):
        b=64.
        c=0.
        iii = cv2.imread(self.image)
        imghsv = cv2.cvtColor(iii, cv2.COLOR_BGR2HSV)
        imghsv = cv2.addWeighted(imghsv, 1. + c/127., imghsv, 0, b-c)
        contrasted = cv2.cvtColor(imghsv, cv2.COLOR_HSV2BGR)
        final = imageobj(self.convtoim(contrasted))
        return final
