
import math
import os

class SentimentClassifier:
	class Document: 
		""" A list of words and their lebel. Labels are 'pos' or 'neg'
		"""
		def __init__(self, words, label):
			self.label = label
			self.words = words



	def __init__(self):
		self.stopWords = []

		self.numberOfDocuments = 0
		self.labelFrequencies = {
			"pos": 0,
			"neg": 0
		}
		self.vocabulary = []
		self.classWordCounts = {
			"pos": {},
			"neg": {}
		}
		self.wordCountPerLabel = {
			"pos": 0,
			"neg": 0
		}

	def train(self, documents):
		for document in documents:
			self.trainBooleanNaiveBayes(document)


	def trainNaiveBayes(self, document):
		self.numberOfDocuments += 1
		self.labelFrequencies[document.label] +=  1

		self.wordCountPerLabel[document.label] += len(document.words)

		for word in document.words:
			self.vocabulary.append(word)
			if word in self.classWordCounts[document.label].keys():
				self.classWordCounts[document.label][word] += 1
			else:
				self.classWordCounts[document.label][word] = 0

	def trainBooleanNaiveBayes(self, document):
		nonDuplicateDocument = document
		nonDuplicateDocument.words = list(set(document.words))
		self.trainNaiveBayes(nonDuplicateDocument)	

	def classifyNaiveBayes(self, words):
		probabilityOfLabelGivenWords = {
			"pos": 0,
			"neg": 0
		}

		for label in probabilityOfLabelGivenWords.keys():
			logLikelihood = math.log(self.labelFrequencies[label]) - math.log(self.numberOfDocuments)
			for word in words:
				if word not in self.vocabulary:
					continue
				wordCount = 0
				if word in self.classWordCounts[label].keys():
					wordCount = self.classWordCounts[label][word]

				wordLikelihood = math.log(wordCount + 1) - math.log(self.wordCountPerLabel[label] + len(self.vocabulary))
				logLikelihood += wordLikelihood

			probabilityOfLabelGivenWords[label] = logLikelihood


		# most likely class
		if probabilityOfLabelGivenWords["pos"] > probabilityOfLabelGivenWords["neg"]:
			return "pos"
		else:
			return "neg"


	def classifyBooleanNaiveBayes(self, words):
		nonDuplicateWords = list(set(words))
		return self.classifyNaiveBayes(nonDuplicateWords)

	def readFile(self, fileName, label):
		documents = []
		file = open(fileName)
		for line in file:
			documents.append(self.Document(line.split(), label))
		file.close()
		return documents

	def readTrainingData(self, trainDirectory):
		documents = []
		posTrainFiles = os.listdir(trainDirectory + "/pos/")
		negTrainFiles = os.listdir(trainDirectory + "/neg/")
		for fileName in posTrainFiles:
			documents.extend(self.readFile(trainDirectory + "/pos/" + fileName, "pos"))
		for fileName in negTrainFiles:
			documents.extend(self.readFile(trainDirectory + "/neg/" + fileName, "neg"))
		return documents



def test():
	classifier = SentimentClassifier()
	
	trainDocuments = classifier.readTrainingData("../sentiment/data/imdb1")
	print "docs... ", len(trainDocuments)
	print "starting training"
	classifier.train(trainDocuments[:100] + trainDocuments[len(trainDocuments) - 100:])
	print "finishing training"

	print "class", classifier.classifyBooleanNaiveBayes(trainDocuments[130].words)
	print classifier.wordCountPerLabel



if __name__ == '__main__':
	test()

		


