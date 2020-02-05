import pytesseract #5.4.0
import cv2 #4.1.0

class TextRecognizer():
	
	def __init__(self):
		self.text = None
		self.size = 500


	""" Tesseract OCR works great on lower sized images. Hence resizing is an important preprocessing step. """
	def ocr(self, img):
		self.im = img
		self.im = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
		self.im = cv2.resize(self.im, (self.size, self.size))
		self.text = pytesseract.image_to_string(self.im)
		return self.text
		

""" im = cv2.imread("/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/TestImages/20200128_223117.jpg",0)
a= TextRecognizer()
text = a.ocr(im)

print("\n\n",text) """