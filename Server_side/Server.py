import socket
import cv2
import numpy as np

from BillReader import BillReader
from CurrencyRecognizer import CurrencyRecognizer
from Summarizer import Summarizer
from TextRecognizer import TextRecognizer
from Bot import Bot

class Server():
    def __init__(self, portNo):
        self.host = socket.gethostname()
        self.port = portNo
        self.size = 4096
        self.sock=socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host,self.port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        print("Client connected")

        self.billReader = BillReader()
        self.currencyRecognizer = CurrencyRecognizer()
        self.currencyRecognizer.configure("/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/DataFiles/yolov3.weights",\
             "/Users/dhavalbagal/Desktop/BE-PROJECT/Sahara/DataFiles/yolov3-tiny.cfg", \
                 ('10','20','50','100','200','500','2000'))
        self.summarizer = Summarizer()
        self.textRecognizer = TextRecognizer()
        self.bot = Bot()


    def fetchData(self):
        data = b""
        try:
            while True:
                dataChunk = self.conn.recv(self.size)
                data+=dataChunk   
                if dataChunk.endswith(b"eof"):
                    data = data[:-3]
                    imgString, command = data.split(b"mof")
                    nparr = np.frombuffer(imgString, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    break
        
            return image, command

        except ValueError:
            return None, ""


    def selectModule(self, image, command):
        msg=""
        intent, _ = self.bot.getIntent(command.decode("utf-8"))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if intent=="CurrencyRecognition":
            msg = self.currencyRecognizer.giveTotal(image)
        elif intent=="BillReading":
            msg = self.billReader.readBill(image)
        elif intent=="TextSummarization":
            text = self.textRecognizer.ocr(image)
            msg = self.summarizer.generateSummary(text)
        elif intent=="BasicTextReading":
            msg = self.textRecognizer.ocr(image)

        return msg


    def sendReply(self, msg):
        msg = ".".join(msg.splitlines())
        msg+='\n'
        self.conn.send(msg.encode())


    def keepListening(self):
        while True:
            image, command = self.fetchData()
            if len(command)!=0:
                msgFromModule = self.selectModule(image, command)
                self.sendReply(msgFromModule)
            else:
                self.sendReply("Something went wrong. Please click the picture again.")


    def restartServer(self):
        self.conn.close()
        self.sock.bind((self.host,self.port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()


    def closeConnection(self):
        self.conn.close()


    def __del__(self):
        self.conn.close()

server = Server(7000)
server.keepListening()

