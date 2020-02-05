from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import OrderedDict

text1 = '''
The adoption of cloud computing into the US Government (USG) and its implementation depend upon a variety of technical and non-technical factors. A fundamental reference point, based on the NIST definition of Cloud Computing, is needed to describe an overall framework that can be used government-wide. This document presents the NIST Cloud Computing Reference Architecture (RA) and Taxonomy (Tax) that will accurately communicate the components and offerings of cloud computing. The guiding principles used to create the RA were 1) develop a vendor-neutral architecture that is consistent with the NIST definition and 2) develop a solution that does not stifle innovation by defining a prescribed technical solution. This solution will create a level playing field for industry to discuss and compare their cloud offerings with the US Government (USG). The resulting reference architecture and taxonomy for cloud computing was developed as an Actor/Role based model that lays out the central elements of cloud computing for Federal CIOs, Procurement Officials and IT Program Managers. The cloudscape is open and diversified and the accompanying taxonomy provides a means to describe it in an unambiguous manner. The RA is presented in two parts: a complete overview of the actors and their roles and the necessary architectural components for managing and providing cloud services such as service deployment, service orchestration, cloud service management, security and privacy. The Taxonomy is presented in its own section and appendices are dedicated to terms and definitions and examples of cloud services. The Overview of the Reference Architecture describes five major actors with their roles & responsibilities using the newly developed Cloud Computing Taxonomy. The five major participating actors are the Cloud Consumer, Cloud Provider, Cloud Broker, Cloud Auditor and Cloud Carrier. These core individuals have key roles in the realm of cloud computing. For example, a Cloud Consumer is an individual or organization that acquires and uses cloud products and services. The purveyor of products and services is the Cloud Provider. Because of the possible service offerings (Software, Platform or Infrastructure) allowed for by the cloud provider, there will be a shift in the level of responsibilities for some aspects of the scope of control, security and configuration. The Cloud Broker acts as the intermediate between consumer and provider and will help consumers through the complexity of cloud service offerings and may also create value-added cloud services as well. The Cloud Auditor provides a valuable inherent function for the government by conducting the independent performance and security monitoring of cloud services. The Cloud Carrier is the organization who has the responsibility of transferring the data akin to the power distributor for the electric grid. The Architectural Components of the Reference Architecture describes the important aspects of service deployment and service orchestration. The overall service management of the cloud is acknowledged as an important element in the scheme of the architecture. Business Support mechanisms are in place to recognize customer management issues like contracts, accounting and pricing and are vital to cloud computing. A discussion on Provisioning and Configuration points out the requirements for cloud systems to be available as needed, metered and have proper SLA management in place. Portability and Interoperability issues for data, systems and services are crucial factors facing consumers in adopting the cloud are also undertaken here. Consumers need confidence in moving their data and services across multiple cloud environments. As a major architectural component of the cloud, Security and Privacy concerns need to be addressed and there needs to be a level of confidence and trust in order to create an atmosphere of acceptance in the cloud‟s ability to provide a trustworthy and reliable system. Security responsibilities, security consideration for different cloud service models and deployment models are also discussed.
'''

class Summarizer():

    """ Stop words are insignificant words like 'a', 'the' which needs to be filtered out before processing the text
            Stemming is the process of producing morphological variants of a root/base word. For e.g, like => likes, likely """


    def __init__(self):
        """ stopwords.words() returns a list of stopwords
            Variable 'stopWords' stores this list in the form of a dictionary (key: word, value: 1) for efficient searching """
        self.stopWords = dict( map( lambda x: (x, 1), stopwords.words("english") ) )
        """ stemmer.stem() function returns the root word of the input text. For e.g: stemmer.stem('likely') returns 'like' """
        self.stemmer = PorterStemmer()
        self.freqTable = dict()
        

    def setupSummarizer(self):
        """ word_tokenize() and sent_tokenize() functions convert a string into a list of words and sentences respectively. """
        self.words = word_tokenize(self.text)

        self.createFreqTable()

        def scoreSentences(sentence):
            words = word_tokenize(sentence)
            count = 0
            totalFrequency = 0
            for word in words:
                frequency = self.freqTable.get(word.lower(), None)
                if frequency != None:
                    count+=1
                    totalFrequency += frequency
            try:
                score = totalFrequency / count
            except ZeroDivisionError:
                score = 0
            return (sentence, score)

        self.sentences = OrderedDict( map( scoreSentences, sent_tokenize(self.text) ) )
        self.avgScore = sum(self.sentences.values())/len(self.sentences.values())


    """ createFreqTable() function creates a dictionary with the word as the key and its frequency as the value """
    def createFreqTable(self):
        
        for word in self.words:
           
            word = word.lower()
            """ Update frequency table only if the word is not a stopword """
            if self.stopWords.get(word, None)== None:

                if self.freqTable.get(word, None)!= None:
                    self.freqTable[word] += 1
                else:
                    self.freqTable[word] = 1


    def generateSummary(self, text, threshold=1):
        summary = ''
        self.text = text
        self.setupSummarizer()
        for sentence, score in self.sentences.items():
            if score>=threshold*self.avgScore:
                summary += sentence

        return summary


""" a = Summarize()
s = a.generateSummary(text1)
#print(a.sentences)
#print(a.sentences['Don’t leave your dreams to chance.'])
print(s) """