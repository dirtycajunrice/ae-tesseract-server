import cv2

def drawDebugRectangle(image: str, xy, wh):
    cv2.rectangle(image, xy, (xy[0] + wh[0], xy[1] + wh[1]), (0, 0, 255), 2)

def showImage(image: str):
    cv2.imshow('output', image)
    cv2.waitKey(0)

#class Anchor:
#    def __init__(self):
#        self.width =