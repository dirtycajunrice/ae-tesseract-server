import cv2
import numpy as np
import pytesseract as pyt
from datetime import datetime

from roster_recorder import helpers

pyt.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class RankingsDecoder():
    def __init__(self):
        self.image = None
        self.image_thr = None

        # Anchor images
        self.anchor_ALL_img = cv2.cvtColor(cv2.imread('images\\anchor_ALL_thresh.png'), cv2.COLOR_BGR2GRAY)

        # OpenCV (cv2) variables
        self.match_method = cv2.TM_SQDIFF_NORMED
        self.threshold_method = cv2.THRESH_TOZERO
        self.image_threshold = 115

        # Coordinate variables for calculating text anchor points
        self.correct_rank_xy, self.num_per_page = (-8, 230), 9
        self.char_h, self.box_h = 16, 80
        self.x_diff_range = [0, 160, 385, 525, 660, 775, 905, 1055]  # rank, name, score, kills, deaths, assists, healing, damage

        # Text sub-image dimensions
        self.text_h = self.box_h - 30
        self.rank_wh = (60, self.text_h)
        self.name_wh = (225, self.text_h)
        self.score_wh = (140, self.text_h)
        self.kills_wh = (135, self.text_h)
        self.deaths_wh = (115, self.text_h)
        self.assists_wh = (130, self.text_h)
        self.healing_wh = (150, self.text_h)
        self.damage_wh = (150, self.text_h)
        self.stats_wh = [self.rank_wh, self.name_wh, self.score_wh, self.kills_wh,
                         self.deaths_wh, self.assists_wh, self.healing_wh, self.damage_wh]

    def read_image(self, raw_image):
        # Read the image using OpenCV and convert to grayscale
        self.image = cv2.cvtColor(cv2.imread(raw_image), cv2.COLOR_BGR2GRAY)
        _, self.image_thr = cv2.threshold(self.image, self.image_threshold, 255, self.threshold_method)

        # Find the anchor sub-image locations within the given image (img)
        return self.anchor_match()

    def anchor_match(self):
        # Match anchor images and create scores
        ALL_match = cv2.matchTemplate(self.anchor_ALL_img, self.image_thr, self.match_method)

        # Get anchor xy from template match. Note: using SQDIFF method, so min score location is used
        _, _, ALL_xy, _ = cv2.minMaxLoc(ALL_match)

        # Calculate the anchor locations for the text we want
        anchor_rank = [ALL_xy[0] + self.correct_rank_xy[0], ALL_xy[1] + self.correct_rank_xy[1]]

        return anchor_rank

    def find_rank(self, anch_xy):
        # Find initial rank box anchor
        attempts = (0, 1, 2)  # If we don't find the scores in 2 moves then something is broken

        for i in attempts:
            rank_found, anchor_xy = self.check_rank_box((anch_xy[0], anch_xy[1] + round(self.box_h / 2) * i))
            if rank_found:
                return anchor_xy

        raise ValueError('Rank text was never found to set anchor point.')

    def check_rank_box(self, anch_xy):
        # Checking if box captures an entire number, then adjusts the box to be centered on the number
        sub_img_thr = self.image_thr[anch_xy[1]:anch_xy[1] + self.rank_wh[1], anch_xy[0]:anch_xy[0] + self.rank_wh[0]]
        white_px = np.argwhere(sub_img_thr > 0)

        if not white_px.any():
            return False, None

        white_y = white_px[:][:, 0]
        min_y, max_y = min(white_y), max(white_y)

        if max_y - min_y >= self.char_h:
            anch_y_adj = max(white_px[:][:, 0]) + round(self.char_h / 2) - round(self.box_h / 2)
            return True, (anch_xy[0], anch_xy[1] + anch_y_adj)
        else:
            return False, None

    def get_text(self, xy, wh):
        # Create the sub-image for where desired text is located
        _, sub_img_thr = cv2.threshold(self.image_thr[xy[1]:xy[1] + wh[1], xy[0]:xy[0] + wh[0]], 115, 255, cv2.THRESH_BINARY_INV)
        # sub_img_thr = cv2.resize(sub_img_thr, None, fx=2, fy=2, interpolation = cv2.INTER_AREA)
        # helpers.showImage(sub_img_thr)

        if not np.any(sub_img_thr[:, :] > 0):
            return None

        # Get text from image using tesseract
        raw_text = pyt.image_to_string(sub_img_thr, lang='eng', config='--psm 7')
        text = raw_text.rstrip('\n\x0c')

        return text

    def extract_rankings(self, anchor_coords):
        # Extract rankings text
        anchor_xy = self.find_rank(anchor_coords)
        x_range, y_range = self.create_rankings_ranges(anchor_xy)
        rankings = []
        player = 0
        stat = 0

        for y in y_range:
            for x in x_range:
                if stat == 0:
                    valid_row, _ = self.check_rank_box((x, y))
                    if not valid_row:
                        break

                text = self.get_text((x, y), self.stats_wh[stat])
                try:
                    rankings[player].append(text)
                except IndexError:
                    rankings.append([text])

                if stat == 7:
                    stat = 0
                    player += 1
                    continue

                stat += 1
        return rankings

    def create_rankings_ranges(self, anchor_coords):
        # Create grid xy range for all members in the army
        a = anchor_coords
        x = [x + a[0] for x in self.x_diff_range]
        y = np.arange(0, self.num_per_page) * self.box_h + a[1]
        return x, y

    def Decode(self, raw_image):
        # Create anchor points for text
        anchor_rank = self.read_image(raw_image)

        # Extract text from image
        rankings = self.extract_rankings(anchor_rank)

        return rankings, str(datetime.now())
