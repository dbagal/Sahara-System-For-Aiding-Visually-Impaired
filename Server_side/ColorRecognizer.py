import cv2 #4.1.0
import numpy as np
from sklearn.cluster import KMeans
import time

class ColorRecognizer():

	def __init__(self):
		self.size = 250000
		self.sampleSize = 500
		self.nclusters = 2

	def dominantColors(self, img):

		img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		""" Reshaping to a list of pixels """
		img = img.reshape((img.shape[0] * img.shape[1], 3))
		idx = np.random.randint(self.size, size=self.sampleSize)
		imgArray = img[idx]

		""" Using k-means to cluster pixels """
		kmeans = KMeans(n_clusters = self.nclusters)
		kmeans.fit(imgArray)

		""" Getting the colors as per dominance order """
		self.colors = kmeans.cluster_centers_

		""" Save labels """
		self.labels = kmeans.labels_
		

		return self.colors.astype(int)

s = time.time()
print("start")
img = cv2.imread("/Users/dhavalbagal/Downloads/color_identification/card2.jpg")

obj = ColorRecognizer()
im = obj.dominantColors(img)
print(im, time.time()-s)