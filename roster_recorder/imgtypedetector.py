import cv2
from roster_recorder import ROSTER, RANKINGS


class ImgTypeDetector():
    def __init__(self):
        # OpenCV (cv2) variables
        self.match_method = cv2.TM_SQDIFF_NORMED
        self.threshold_method = cv2.THRESH_TOZERO
        self.image_threshold = 115

        # Anchor images
        self.anchor_armygroups_thresh = cv2.cvtColor(cv2.imread('images\\anchor_armygroups_thresh.png'), cv2.COLOR_BGR2GRAY)
        self.anchor_ALL_img = cv2.cvtColor(cv2.imread('images\\anchor_ALL_thresh.png'), cv2.COLOR_BGR2GRAY)

    def Detect(self, raw_image):
        # Open image and create a threshold image
        image = cv2.cvtColor(cv2.imread(raw_image), cv2.COLOR_BGR2GRAY)
        _, image_thr = cv2.threshold(image, self.image_threshold, 255, self.threshold_method)

        # Match anchor images
        armygroups_match = cv2.matchTemplate(self.anchor_armygroups_thresh, image_thr, self.match_method)
        ALL_match = cv2.matchTemplate(self.anchor_ALL_img, image_thr, self.match_method)

        # Get scores
        armygroups_min, _, _, _ = cv2.minMaxLoc(armygroups_match)
        ALL_min, _, _, _ = cv2.minMaxLoc(ALL_match)

        # Identify if roster or rankings screenshot
        if ALL_min < armygroups_min:
            return RANKINGS
        else:
            return ROSTER
