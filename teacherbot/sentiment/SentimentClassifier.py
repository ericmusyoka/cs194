
class SentimentClassifier:
	class Document: 
		""" A list of words and their lebel. Labels are 'pos' or 'neg'
		"""
		def __init__(self):
			self.label = ''
			self.words = []



	def __init__(self):
		self.stopWords = []

		self.numberOfDocuments = 0
		self.labelFrequencies = {
			"pos": 0,
			"neg": 0
		}
		self.vocabulary = []
		self.classWordCounts = {
			"pos": {}
			"neg": {}
		}

		trainBinaryNaiveBayes()

	def train(documents):
		for document in documents:
			trainBinaryNaiveBayes(document)


	def trainNaiveBayes(self, document):
		numberOfDocuments += 1
		labelFrequencies[document.label] +=  1

		for word in document.words:
			self.vocabulary.append(word)
			if word in self.classWordCounts[document.label]:
				self.classWordCounts[document.label][word] += 1
			else:
				self.classWordCounts[document.label][word] = 0

	def trainBooleanNaiveBayes(document):
		nonDuplicateDocument = document
		nonDuplicateDocument.words = list(set(document.words))
		trainNaiveBayes(nonDuplicateDocument)	

	def classifyDocument(self, document):
		


