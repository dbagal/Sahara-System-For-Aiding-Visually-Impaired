import cv2 #4.1.0
import numpy as np #1.16.4
from DetectObject import DetectObject
import time

class CurrencyRecognizer():
	
	def __init__(self):
		self.detectObj = DetectObject()
		self.uniquenessDist = 400


	def configure(self, weights, config, classNames):
		""" self.weights: path to the yolo .weights file  
			self.config: path to the yolo .cfg file 
			self.classNames: list of class names. Only integer classnames are allowed for CurrencyRecognizer. """
		self.detectObj.configure(weights, config, classNames)
		self.classNames = classNames
		self.noOfClasses = len(self.classNames)


	""" @input: [6,6,1,2,2,6]
		@output: {2: [3, 4], 6: [0, 1, 5]} """
	def groupDuplicates(self, dupList):
		elemDict = dict()
		for index, elem in enumerate(dupList):
			indicesOfElem = elemDict.get(elem, None)
			if indicesOfElem==None:
				elemDict[elem] = [index, ]
			else:
				indicesOfElem.append(index)
				elemDict[elem] = indicesOfElem
		return elemDict


	""" @parameters: 
			pointList: [(5,3), (4,6), (7,8)]"""
	def getMaxDist(self, pointList):
		bboxes = np.array(pointList) 
		distMatrix = np.asarray( [[np.linalg.norm(p1-p2) for p2 in bboxes] for p1 in bboxes] )
		return np.max(distMatrix)


	def getUniquenessThresh(self, predictions):
		minDist = 99999
		n = len(predictions)

		distMatrix =dict()
		for i in range(n):
			for j in range(i, n):
				boundingBoxes = predictions[i]['boundingBoxes']
				centerCoords1 = ( (boundingBoxes[0]+boundingBoxes[2])/2, (boundingBoxes[1]+boundingBoxes[3])/2  )
				boundingBoxes = predictions[j]['boundingBoxes']
				centerCoords2 = ( (boundingBoxes[0]+boundingBoxes[2])/2, (boundingBoxes[1]+boundingBoxes[3])/2  )
				dist = np.linalg.norm(np.array(centerCoords1) - np.array(centerCoords2) )

				distMatrix[(i,j)] = dist

				if dist<minDist:
					minDist = dist
		""" 1.5 times the minimum distance is the uniqueness threshold. """
		return distMatrix, minDist*1.5 
	
	def giveTotal(self, image):
		self.currencyDetections = dict()
		self.predictions = self.detectObj.detect(image)
		""" @example self.predictions = [{'classID': 3, 'confidence': 0.9957972764968872, 'boundingBoxes': (201, 282, 282, 339)}, {'classID': 5, 'confidence': 0.8785867691040039, 'boundingBoxes': (232, 157, 318, 213)}]  """
		
		distMatrix, minDist = self.getUniquenessThresh(self.predictions)
		
		n = len(self.predictions)

		for i in range(n):
			pointInNeighbourhoodExists = False
			for j in range(i,n):
				dist = distMatrix[(i,j)]
				if dist<=minDist:
					pointInNeighbourhoodExists = True
					break

			if not pointInNeighbourhoodExists:
				del self.predictions[i]

		n = len(self.predictions)
		totalAmount = 0
		if n!=0:
			currencyCount = dict()

			for prediction in self.predictions:
				amount = self.classNames[prediction["classID"]]
				totalAmount += int(amount)
				if currencyCount.get(amount, None)==None:
					currencyCount[amount] = 1
				else:
					currencyCount[amount] += 1

			if n==1:
				for currency, _ in currencyCount.items():
					reply = "I see a note of INR "+currency
					return reply
			else:
				reply = "I see in all "+str(len(self.predictions))+" notes of which "

			""" @example currencyCount = {'10':2, '500':3} """
			for currency, count in currencyCount.items():
				if count==1:
					text = str(count)+" is of"+" INR "+currency+", "
				else:
					text = str(count)+" are of"+" INR "+currency+", "
				reply += text
		else:
			reply= "I am not able to detect the currency. Please try again"
		return reply


