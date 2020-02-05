import cv2 #4.1.0
import re   #2.2.1
from TextRecognizer import TextRecognizer

class BillReader:

    def __init__(self):
        self.text = None
        self.size = 500
        self.textRecognizer = TextRecognizer()
        self.products = dict()


    """ Note: A product name in a bill is always followed by a floating number indicating either the tax or the amount.\
        Hence fetching all the characters before the first floating number will give the product name."""
    def extractProductNames(self):
        productNameRegex = '^(.*?)[0-9]+[.][0-9]+'
        productPrice = '[0-9]+[.][0-9]+'

        """ Every record contains productName followed by the tax amount, quantity, price etc."""
        records = self.text.splitlines()
        
        for record in records:
            try:
                """ When capturing a group in a regular expression, you need to put parentheses around the group that you aim to capture. \
                    Also, you need to pass the index of the group you want to capture to the group() method. """
                productName = re.search(productNameRegex, record).group(1)
                """ Assumption: Last floating number in a record is the price of the product. """
                self.products[productName] = re.findall(productPrice, record)[-1]
            except:
                """ Ignore if no product is found in a record """
                pass


    def readBill(self, img):
        self.im = img
        self.text = self.textRecognizer.ocr(self.im)
        self.extractProductNames()
        if len(self.products)!=0:
            reply = ""
            for name, price in self.products.items():
                reply+= name+" costs INR "+str(price)+". "
        else:
            reply = "I am not able to read the bill. Please try again."
        return reply

""" im = cv2.imread("/Users/dhavalbagal/Desktop/BE-PROJECT/temp4.jpg",0)
a= BillReader()
p = a.readBill(im) 
print(p) """
