import cv2

from roster_recorder import IMG_WIDTH, IMG_HEIGHT


def drawDebugRectangle(image: str, maxVal):
    cv2.rectangle(image, maxVal, (maxVal[0] + IMG_WIDTH, maxVal[1] + IMG_HEIGHT), (0, 0, 255), 2)

def showImage(image: str):
    cv2.imshow('output', image)
    cv2.waitKey(0)



#class Anchor:
#    def __init__(self):
#        self.width =