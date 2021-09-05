import csv
import cv2

import numpy as np
import pytesseract as pyt

from roster_recorder import helpers
from roster_recorder import INVASION, WAR

pyt.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class Decoder():
    def __init__(self):
        self.image = None
        self.image_wartype = None

        # Anchor images
        self.anchor_wartime_img = cv2.cvtColor(cv2.imread('images\\anchor_wartime_gray.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_invtime_img = cv2.cvtColor(cv2.imread('images\\anchor_invasiontime_gray.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_location_img = cv2.cvtColor(cv2.imread('images\\anchor_location_gray.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_armygroups_img = cv2.cvtColor(cv2.imread('images\\anchor_armygroups_gray.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_standbylist_img = cv2.cvtColor(cv2.imread('images\\anchor_standbylist_gray.png'), cv2.COLOR_BGR2GRAY)

        # cv2.matchTemplate args
        self.method = cv2.TM_SQDIFF_NORMED

        # Coordinate variables for calculating text anchor points
        self.correct_timedate_xy, self.correct_timetime_xy = (-95, 43), (-95, 81)
        self.correct_loc_xy = (-95, 43)
        self.correct_army_xy, self.x_diff_army, self.y_diff_army, self.y_diff_army_r2 = (73, 167), 298, 57, 414
        self.correct_standby_xy, self.y_diff_standby, self.standby_num_per_page = (96, 78), 49, 19

        # Text sub-image dimensions
        self.timedate_wh, self.timetime_wh = (450, 30), (450, 30)
        self.location_wh = (350, 34)
        self.army_wh = (142, 35)
        self.standby_wh = (157, 31)

    def read_image(self, raw_image):
        self.image = cv2.cvtColor(cv2.imread(raw_image), cv2.COLOR_BGR2GRAY)
        # Find the anchor sub-image locations within the given image (img)
        return self.anchor_match()

    def anchor_match(self):
        # match
        wartime_match = cv2.matchTemplate(self.anchor_wartime_img, self.image, self.method)
        invtime_match = cv2.matchTemplate(self.anchor_invtime_img, self.image, self.method)
        location_match = cv2.matchTemplate(self.anchor_location_img, self.image, self.method)
        armygroups_match = cv2.matchTemplate(self.anchor_armygroups_img, self.image, self.method)
        standbylist_match = cv2.matchTemplate(self.anchor_standbylist_img, self.image, self.method)

        # Get anchor xy from template match
        wartime_min, _, wartime_xy, _ = cv2.minMaxLoc(wartime_match)
        invtime_min, _, invtime_xy, _ = cv2.minMaxLoc(invtime_match)
        _, _, location_xy, _ = cv2.minMaxLoc(location_match)
        _, _, armygroups_xy, _ = cv2.minMaxLoc(armygroups_match)
        _, _, standbylist_xy, _ = cv2.minMaxLoc(standbylist_match)

        # Identify if war or invasion screenshot
        if wartime_min < invtime_min:
            time_xy = wartime_xy
            self.image_wartype = WAR
        else:
            time_xy = invtime_xy
            self.image_wartype = INVASION

        anchor_time = [(time_xy[0] + self.correct_timedate_xy[0], time_xy[1] + self.correct_timedate_xy[1]),
                       (time_xy[0] + self.correct_timetime_xy[0], time_xy[1] + self.correct_timetime_xy[1])]
        anchor_loc = [location_xy[0] + self.correct_loc_xy[0], location_xy[1] + self.correct_loc_xy[1]]
        anchor_army = [armygroups_xy[0] + self.correct_army_xy[0], armygroups_xy[1] + self.correct_army_xy[1]]
        anchor_standby = [standbylist_xy[0] + self.correct_standby_xy[0], standbylist_xy[1] + self.correct_standby_xy[1]]

        return anchor_time, anchor_loc, anchor_army, anchor_standby


    def get_name(self, xy, wh):
        sub_image = self.image[xy[1]:xy[1] + wh[1], xy[0]:xy[0] + wh[0]] # Note, dimensions are (y, x) on cv images
        helpers.showImage(sub_image)
        raw_name = pyt.image_to_string(sub_image, lang='eng', config='--psm 6')
        name = raw_name.rstrip('\n\x0c')
        return name

    def extract_time(self, anchor_coords):
        time = []
        time.append(self.get_name(anchor_coords[0], self.timedate_wh))
        time.append(self.get_name(anchor_coords[1], self.timetime_wh))
        return time

    def extract_location(self, anchor_coords):
        location = []
        location.append(self.get_name(anchor_coords, self.location_wh))
        return location

    def extract_army(self, anchor_coords):
        x_range, y_range = self.create_roster_ranges(anchor_coords)
        roster = []
        group = 0
        player = 0
        for x in x_range:
            for y in y_range:
                try:
                    roster[group].append(self.get_name((x, y), self.army_wh))
                except IndexError:
                    roster.append([self.get_name((x, y), self.army_wh)])
                # print(f"Adding Player {player} to group {group}")
                if player == 4:
                    player = 0
                    group += 1
                    continue

                player += 1
        return roster

    def create_roster_ranges(self, anchor_coords):
        a = anchor_coords
        tmparray = np.arange(0, 5) * self.y_diff_army + a[1]
        y = np.concatenate((tmparray, tmparray + self.y_diff_army_r2))
        x = np.arange(0, 5) * self.x_diff_army + a[0]
        return x, y

    def extract_standby(self, anchor_coords):
        standby = []
        for y_adjust in np.arange(0, self.standby_num_per_page):
            standby.append(self.get_name((anchor_coords[0], anchor_coords[1] + (y_adjust * self.y_diff_standby)),
                                          self.standby_wh))
        return standby

    def Decode(self, raw_image):
        anchor_time, anchor_loc, anchor_army, anchor_standby = self.read_image(raw_image)

        time = self.extract_time(anchor_time)
        location = self.extract_location(anchor_loc)
        army = self.extract_army(anchor_army)
        standby = self.extract_standby(anchor_standby)

        return self.image_wartype, time, location, army, standby

# open image


