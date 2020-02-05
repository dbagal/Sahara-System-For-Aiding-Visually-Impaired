import cv2 #4.1.0
import numpy as np #1.16.4
from DetectObject import DetectObject
import time

class CurrencyRecognizer():
	
	def __init__(self):
		self.detectObj = DetectObject()
		self.recognitionThresh = 0.6
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


	def setUniquenessDist(self):
		classIds = [prediction['classID'] for prediction in self.predictions]
		bboxes = [ ( ( bbox['boundingBoxes'][0]+bbox['boundingBoxes'][2])/2, (bbox['boundingBoxes'][1]+bbox['boundingBoxes'][3])/2 ) \
			for bbox in self.predictions ]
		maxList = []
		duplicates = self.groupDuplicates(classIds)
		for _, dupIndices in duplicates.items():
			maxDist = self.getMaxDist([bboxes[i] for i in dupIndices])
			maxList.append(maxDist)
		
		try:
			self.uniquenessDist = max(maxList)
		except ValueError:
			self.uniquenessDist = None


	def giveTotalCount(self, image):
		self.currencyDetections = dict()
		self.predictions = self.detectObj.detect(image)
		self.setUniquenessDist()

		if self.uniquenessDist != None:
			for prediction in self.predictions:
				classId = prediction['classID']
				confidence = prediction['confidence']
				boundingBoxes = prediction['boundingBoxes']
				centerCoords = ( (boundingBoxes[0]+boundingBoxes[2])/2, (boundingBoxes[1]+boundingBoxes[3])/2  )
				""" Update self.currencyDetections """
				existingDetection = self.currencyDetections.get(classId, None)
				if existingDetection==None:
					count = 1
					self.currencyDetections[classId] = (confidence, boundingBoxes, count)
				else:
					bboxes = existingDetection[1]
					count = existingDetection[2]
					existingCenterCoords = ( (bboxes[0]+bboxes[2])/2, (bboxes[1]+bboxes[3])/2 )
					a = np.array(existingCenterCoords)
					b = np.array(centerCoords)
					dist = np.linalg.norm(a-b)
					if dist<=self.uniquenessDist:
						count+=1
						self.currencyDetections[classId] = (confidence, boundingBoxes, count)
			""" @example self.currencyDetections: {1: (0.9916291832923889, (129, 367, 177, 418), 3)} """
			
			totalAmount = 0
			if len(self.currencyDetections)!=0:
				reply = "I see "
				for classid, value in self.currencyDetections.items():
					currency = self.classNames[classid]
					count = value[2]
					totalAmount += int(currency)*count
					if count==1:
						text = str(count)+" note of"+" INR "+currency+", "
					else:
						text = str(count)+" notes of"+" INR "+currency+", "+"and the total amount is INR "+str(totalAmount)
				reply += text
		else:
			reply= "I am not able to detect the currency. Please try again"
		return reply


""" obj = CurrencyRecognizer()
obj.configure("/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/yolov2-tiny_22700.weights", "/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/yolov2-tiny.cfg", ('100', '200', '500'))

s = time.time()
im = cv2.imread("/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/TestImages/20200128_213444.jpg")
im = cv2.resize(im,(416,416))
p = obj.giveTotalCount(im)
print(p, time.time()-s) """

