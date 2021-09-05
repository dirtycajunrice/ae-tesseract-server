import csv
import cv2

import numpy as np
import pytesseract as pyt

from roster_recorder import helpers
from roster_recorder import IMG_WIDTH, IMG_HEIGHT

pyt.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class Decoder():
    def __init__(self):
        self.image = None
        self.method = cv2.TM_SQDIFF_NORMED
        self.anchor = cv2.imread('images\\roster_anchor.png')
        self.x_diff, self.y_diff, self.y_diff_r2 = 298, 57, 414

    def read_image(self, raw_image):
        self.image = cv2.imread(raw_image)
        # Find the anchor sub-image location within the given image (img)
        anchor_loc = cv2.matchTemplate(self.anchor, self.image, self.method)
        # Get xy from the anchor location
        _, _, maxVal, _ = cv2.minMaxLoc(anchor_loc)
        return [maxVal[1] + 53, maxVal[0] + 68]

    def create_ranges(self, anchor_coords):
        a = anchor_coords
        tmparray = np.arange(0, 5) * self.y_diff + a[0]
        y = np.concatenate((tmparray, tmparray + self.y_diff_r2))
        x = np.arange(0, 5) * self.x_diff + a[1]
        return x, y

    def GetName(self, x, y):
        sub_image = self.image[y:y + IMG_HEIGHT, x:x + IMG_WIDTH]
        raw_name = pyt.image_to_string(sub_image, lang='eng', config='--psm 6')
        name = raw_name.rstrip('\n\x0c')
        return name

    def Decode(self, raw_image):
        anchor_coords = self.read_image(raw_image)
        return self.create_ranges(anchor_coords)

# open image



