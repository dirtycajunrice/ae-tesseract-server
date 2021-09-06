import re
import cv2
import numpy as np
import pytesseract as pyt
from datetime import datetime

from roster_recorder import helpers
from roster_recorder import INVASION, WAR

pyt.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class RosterDecoder():
    def __init__(self):
        self.image = None
        self.image_wartype = None

        # Anchor images
        self.anchor_wartime_img = cv2.cvtColor(cv2.imread('images\\anchor_wartime_thresh.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_invtime_img = cv2.cvtColor(cv2.imread('images\\anchor_invasiontime_thresh.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_location_img = cv2.cvtColor(cv2.imread('images\\anchor_location_thresh.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_armygroups_img = cv2.cvtColor(cv2.imread('images\\anchor_armygroups_thresh.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_standbylist_img = cv2.cvtColor(cv2.imread('images\\anchor_standbylist_thresh.png'), cv2.COLOR_BGR2GRAY)

        # OpenCV (cv2) variables
        self.match_method = cv2.TM_SQDIFF_NORMED
        self.threshold_method = cv2.THRESH_TOZERO
        self.image_threshold = 85

        # Coordinate variables for calculating text anchor points
        self.correct_timedate_xy, self.correct_timetime_xy = (-95, 41), (-95, 79)
        self.correct_loc_xy = (-95, 41)
        self.correct_army_xy, self.x_diff_army, self.y_diff_army, self.y_diff_army_r2 = (74, 165), 298, 57, 414
        self.correct_standby_xy, self.y_diff_standby, self.standby_num_per_page = (94, 78), 49, 19
        self.correct_page_xy = (85, 1038)

        # Text sub-image dimensions
        self.timedate_wh, self.timehour_wh = (390, 30), (390, 30)
        self.location_wh = (350, 34)
        self.army_wh = (144, 30)
        self.standby_wh = (157, 36)
        self.page_wh = (108, 34)

    def read_image(self, raw_image):
        # Read the image using OpenCV and convert to grayscale
        self.image = cv2.cvtColor(cv2.imread(raw_image), cv2.COLOR_BGR2GRAY)

        # Find the anchor sub-image locations within the given image (img)
        return self.anchor_match()

    def anchor_match(self):
        # Match anchor images and create scores
        wartime_match = cv2.matchTemplate(self.anchor_wartime_img, self.image, self.match_method)
        invtime_match = cv2.matchTemplate(self.anchor_invtime_img, self.image, self.match_method)
        location_match = cv2.matchTemplate(self.anchor_location_img, self.image, self.match_method)
        armygroups_match = cv2.matchTemplate(self.anchor_armygroups_img, self.image, self.match_method)
        standbylist_match = cv2.matchTemplate(self.anchor_standbylist_img, self.image, self.match_method)

        # Get anchor xy from template match. Note: using SQDIFF method, so min score location is used
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

        # Calculate the anchor locations for the text we want
        anchor_time = [(time_xy[0] + self.correct_timedate_xy[0], time_xy[1] + self.correct_timedate_xy[1]),
                       (time_xy[0] + self.correct_timetime_xy[0], time_xy[1] + self.correct_timetime_xy[1])]
        anchor_loc = [location_xy[0] + self.correct_loc_xy[0], location_xy[1] + self.correct_loc_xy[1]]
        anchor_army = [armygroups_xy[0] + self.correct_army_xy[0], armygroups_xy[1] + self.correct_army_xy[1]]
        anchor_standby = [standbylist_xy[0] + self.correct_standby_xy[0], standbylist_xy[1] + self.correct_standby_xy[1]]
        anchor_page = [standbylist_xy[0] + self.correct_page_xy[0], standbylist_xy[1] + self.correct_page_xy[1]]  # Page number uses standbylist_xy to derive anchor point

        return anchor_time, anchor_loc, anchor_army, anchor_standby, anchor_page


    def get_text(self, xy, wh):
        # Create the sub-image for where desired text is located
        sub_image = self.image[xy[1]:xy[1] + wh[1], xy[0]:xy[0] + wh[0]]  # Note, dimensions are (y, x) on cv images
        _, sub_image_thresh = cv2.threshold(sub_image, self.image_threshold, 255, cv2.THRESH_BINARY_INV)

        # If entire image is white, return none
        if not np.any(sub_image_thresh[:, :] == 0):
            return None

        # Get text from image using tesseract
        raw_text = pyt.image_to_string(sub_image, lang='eng', config='--psm 6')
        text = raw_text.rstrip('\n\x0c')

        return text

    def extract_time(self, anchor_coords):
        # Extract date/time text
        month_day = (self.get_text(anchor_coords[0], self.timedate_wh)).split(", ")[1]
        hour = (self.get_text(anchor_coords[1], self.timehour_wh)).split()
        # timezone = hour[5].replace("(", "").replace(")", "")  # timezone - can't get strptime to read this...

        datestring = " ".join([month_day, " ".join(hour[0].split(":")), hour[1]])
        return [self.determine_year(datestring)]

    def determine_year(self, datestring):
        # Year isn't included on war/invasion image
        # Determining year to avoid wrong year in case war is not same year as images parsed
        this_year = datetime.today().year
        last_year = datetime.today().year - 1

        date_this_year = datetime.strptime(" ".join([datestring, str(this_year)]), '%b %d %I %M %p %Y')
        date_last_year = datetime.strptime(" ".join([datestring, str(last_year)]), '%b %d %I %M %p %Y')

        if datetime.today() < date_this_year:
            return date_last_year
        else:
            return date_this_year

    def extract_location(self, anchor_coords):
        # Extract location text
        location = []
        location.append(self.get_text(anchor_coords, self.location_wh))
        return location

    def extract_army(self, anchor_coords):
        # Extract army text
        x_range, y_range = self.create_roster_ranges(anchor_coords)
        army = []
        group = 0
        player = 0
        for x in x_range:
            for y in y_range:
                text = self.get_text((x, y), self.army_wh)
                if text is not None:
                    try:
                        army[group].append(text)
                    except IndexError:
                        army.append([self.get_text((x, y), self.army_wh)])
                # print(f"Adding Player {player} to group {group}")
                if player == 4:
                    player = 0
                    group += 1
                    continue

                player += 1
        return army

    def create_roster_ranges(self, anchor_coords):
        # Create grid xy range for all members in the army
        a = anchor_coords
        tmparray = np.arange(0, 5) * self.y_diff_army + a[1]
        y = np.concatenate((tmparray, tmparray + self.y_diff_army_r2))
        x = np.arange(0, 5) * self.x_diff_army + a[0]
        return x, y

    def extract_standby(self, anchor_coords):
        # Extract standby list text
        standby = []
        for y_adjust in np.arange(0, self.standby_num_per_page):
            text = self.get_text((anchor_coords[0], anchor_coords[1] + (y_adjust * self.y_diff_standby)),
                                 self.standby_wh)
            if text is not None:
                standby.append(text)

        return standby

    def extract_page(self, anchor_coords):
        # Extract page list text
        page_txt = []
        page_txt.append(self.get_text(anchor_coords, self.page_wh))
        page = re.findall(r'\d+', page_txt[0])
        return page

    def Decode(self, raw_image):
        # Create anchor points for text
        anchor_time, anchor_loc, anchor_army, anchor_standby, anchor_page = self.read_image(raw_image)

        # Extract text from image
        time = self.extract_time(anchor_time)
        location = self.extract_location(anchor_loc)
        army = self.extract_army(anchor_army)
        standby = self.extract_standby(anchor_standby)
        page = self.extract_page(anchor_page)

        return self.image_wartype, time, location, army, standby, page

