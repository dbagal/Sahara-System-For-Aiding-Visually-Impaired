import cv2
import numpy as np

class BlurrDetector():
    def __init__(self):
        self.blurrCoefficient = None
        self.kernel = np.array([[0,1,0],[1,-4,1],[0,1,0]])

    def getBlurrCoefficient(self, image):
        self.blurrCoefficient =  cv2.Laplacian(image, cv2.CV_64F).var()
        return self.blurrCoefficient

im = cv2.imread("/Users/dhavalbagal/Desktop/BE-PROJECT/temp6.png",0)
obj = BlurrDetector()
print(obj.getBlurrCoefficient(im))