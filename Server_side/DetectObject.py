import cv2 #4.1.0
import numpy as np #1.16.4

class DetectObject():
	
	def __init__(self):
		
		self.weights = None
		self.config = None
		self.classNames = None

		self.inputWidth = 416
		self.inputHeight = 416
		self.scale = 0.00392
		self.confThreshold = 0.5
		self.nmsThreshold = 0.4
		

	def configure(self, weights, config, classNames):
		""" self.weights: path to the yolo .weights file  
			self.config: path to the yolo .cfg file 
			self.classNames: list of class names """
		self.weights = weights
		self.config = config
		self.classNames = classNames

		""" Read pre-trained model and config file """
		self.net = cv2.dnn.readNet(self.weights, self.config)

		
	def detect(self, image):
		self.outputPredictions = None
		self.predictions = dict()
		self.totalBBoxes = 0

		self.image = image
		self.imgWidth = self.image.shape[1]
		self.imgHeight = self.image.shape[0]

		""" blobFromImage() functon preprocesses the image before feeding it to the neural network """
		self.inputBlob = cv2.dnn.blobFromImage(self.image, self.scale, size=(self.inputWidth, self.inputHeight), \
						mean=(0,0,0), swapRB=True, crop=False)
		""" Set input blob for the network """
		self.net.setInput(self.inputBlob)

		""" Assumption: Last layer is the output layer """
		outputLayer = self.net.getLayerNames()[-1] 

		""" Run inference through the network and gather predictions from output layers. 
			If we don’t specify the output layer names, by default, it will return the predictions only from final output layer. 
			Any intermediate output layer will be ignored."""
		self.outputPredictions = self.net.forward(outputLayer)

		""" 'boxes' and 'confidences' are temporary lists which are to be used as parameters for NMSBoxes() function """
		boxes = []
		confidences = []

		for detection in self.outputPredictions:
			
				classProbabilities = detection[5:]
				predictedClassID = np.argmax(classProbabilities)

				""" Here the confidence is explicitly typecast to 'float' 
					since the 'classProbabilities' that are returned have datatype as 'numpy.float32'  """
				predictedClassConfidence = float(classProbabilities[ predictedClassID ])

				if predictedClassConfidence > self.confThreshold:
					
					""" boxWidth and boxHeight can be greater than imgWidth and imgHeight respectively. 
						It could be due to not enough training or because of your object anchors being off."""
					x = detection[0]
					y = detection[1]
					w = detection[2]
					h = detection[3]

					Xmin = int( (x-w/2)*self.imgWidth )
					Ymin = int( (y-h/2)*self.imgHeight )
					Xmax = int( (x+w/2)*self.imgWidth )
					Ymax = int( (y+h/2)*self.imgHeight )
					boxWidth = int(w*self.imgWidth)
					boxHeight = int(h*self.imgHeight)

					self.predictions[self.totalBBoxes] = {"classID":predictedClassID, \
						"confidence":predictedClassConfidence, "boundingBoxes": (Xmin, Ymin, Xmax, Ymax)}
					self.totalBBoxes += 1
					boxes.append((Xmin, Ymin, boxWidth, boxHeight))
					confidences.append(predictedClassConfidence)

		""" Filtering the predicted bounding boxes using non-max suppression """
		nmsOutput = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
		indices = list(map(lambda x: x[0], nmsOutput))
		self.predictions = [self.predictions[i] for i in indices]
		
		""" self.predictions format => [{'classID': class_id, 'boundingBoxes': bbox_dimensions, 'confidence':confidence }] \
			@example => [{'classID': 6, 'confidence': 0.8540265560150146, 'boundingBoxes': (160, -26, 1127, 847)}]"""
		return self.predictions



