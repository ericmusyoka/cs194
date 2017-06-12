
from __future__ import division
import math
import Queue
import os
import json

from PorterStemmer import PorterStemmer

class BotBrain:
	def __init__(self):
		self.vocabulary = []
		self.invertedIndex = {} 
		self.documents = []
		self.documentsUnstemmed = []
		self.tfidf = {} # {word: { docId: tfidf}}
		self.docIdToFilename = {}

		self.stemmer = PorterStemmer()
		self.stopWords = []


	def readData(self, dataDirectory):
		filenames = []
		for filename in os.listdir(dataDirectory):
			if filename.endswith("txt") and not filename.startswith("."):
				filenames.append(filename)

		filenames = filenames[:100]

		for docId, filename in enumerate(filenames):
			words = []
			file = open(dataDirectory + filename, "r")
			for line in file:
				line = line.lower()
				line = [x.strip() for x in line.split()]
				line = [x for x in line if x != ""]
				words.extend(line)
			file.close()
			self.documents.append(words)
			self.docIdToFilename[str(docId)] = filename

		for document in self.documents:
			self.vocabulary.extend(document)

		self.vocabulary = self.getUnique(self.vocabulary)

	#Line as a doc
	def readData2(self, dataDirectory):
		#stop words
		file = open("sentiment/data/imdb1/english.stop" , "r")
		self.stopWords = file.read().split()
		self.stopWords = [word.strip() for word in self.stopWords]
		self.stopWords = [x for x in self.stopWords if x != ""]
		self.stopWords = [self.stemmer.stem(word) for word in self.stopWords]

		filenames = []
		for filename in os.listdir(dataDirectory):
			if filename.endswith("txt") and not filename.startswith("."):
				filenames.append(filename)

		filenames = filenames[:20]

		for filename in filenames:
			file = open(dataDirectory + filename, "r")
			lines = file.read().split(".")
			for docId, line in enumerate(lines):
				line = line.lower()
				line = [x.strip() for x in line.split()]
				line = [x for x in line if x != ""]
				self.documentsUnstemmed.append(line)
				line = [self.stemmer.stem(word) for word in line]
				line = self.removeStopWords(line)
				self.documents.append(line)
				self.docIdToFilename[str(docId)] = filename
			file.close()

		for document in self.documents:
			self.vocabulary.extend(document)

		self.vocabulary = self.getUnique(self.vocabulary)


	def getUnique(self, words):
		uniqWords = set(words)
		return list(uniqWords)

	"""
		Call after indexing
	"""
	def computeTFIDF(self):
		print "Computing tfidf..."

		for count, docId in enumerate(self.documents.keys()):
			if count % 100 == 0 :
				print "-- Doc number ", count, " of ", len(self.documents)

			document = self.documents[str(docId)]
			for word in document:
				wordCountInDocument = len(self.invertedIndex[word][str(docId)])
				if word not in self.tfidf.keys():
					self.tfidf[word] = {}
				if str(docId) not in self.tfidf[word].keys():
					self.tfidf[word][str(docId)] = 0
				self.tfidf[word][str(docId)] += wordCountInDocument

		for word in self.tfidf.keys():
			documentsWithWord = self.tfidf[word].keys()
			idf = math.log(len(self.documents), 10) / len(documentsWithWord)
			for docId in documentsWithWord:
				tf = 1 + math.log(self.tfidf[word][str(docId)], 10)
				self.tfidf[word][str(docId)] = tf * idf


	def getTFIDF(self, word, documentId):
		if word not in self.tfidf.keys():
			return 0.0

		if str(documentId) not in self.tfidf[word].keys():
			return 0.0

		return self.tfidf[word][str(documentId)]

	def index(self):
		print "starting indexing..."

		# Populating invertedIndex  { word : { docId: [positions]}}
		for word in self.vocabulary:
			self.invertedIndex[word] = {}

		for docId, document in enumerate(self.documents):
			for wordIndex, word in enumerate(document):
				if str(docId) not in self.invertedIndex[word].keys():
					self.invertedIndex[word][str(docId)] = []
				self.invertedIndex[word][str(docId)].append(wordIndex)

		# Creating doc id to doc words map {docId: set(docWords)}
		idToDocWords = {}
		for docId, document in enumerate(self.documents):
			idToDocWords[str(docId)] = document
		self.documents = idToDocWords

		idToDocWords = {}
		for docId, document in enumerate(self.documentsUnstemmed):
			idToDocWords[str(docId)] = document
		self.documentsUnstemmed = idToDocWords

		print "finished indexing..."

	def getPosting(self, word):
		"""
		Return a list of document ids where the word occurs
		"""
		if word in self.invertedIndex:
			return self.invertedIndex[word].keys()
		else:
			return []


	def booleanRetrieve(self, query):
		""" 
		Given a list words,find all documemts where all the words appeear
		in any order
		"""
		docs = []
		if len(query) == 0:
			return docs

		# Intersect algorithm
		docs = self.getPosting(query[0])
		if len(query) == 1:
			docs.sort()
			return docs

		posting1 = []
		posting2 = []

		postingIndex1 = 0
		postingIndex2 = 0

		for queryIndex in range(1, len(query)):
			posting1 = docs
			docs = []
			posting2 = self.getPosting(query[queryIndex])
			postingIndex1 = 0
			postingIndex2 = 0

			if len(posting1) == 0 or len(posting2) == 0:
				return []

			posting1.sort()
			posting2.sort()

			while postingIndex1 != len(posting1) and postingIndex2 != len(posting2):
				posting1DocId = posting1[postingIndex1]
				posting2DocId = posting2[postingIndex2]
				if posting1DocId == posting2DocId:
					docs.append(posting1DocId)
					postingIndex1 += 1
					postingIndex2 += 1
				elif posting1DocId < posting2DocId:
					postingIndex1 += 1
				else:
					postingIndex2 += 1


			docs.sort()
			return docs

	def phraseRetrieve(self, query):
		docs = []
		if len(query) == 0:
			return docs

		# Intersect algorithm
		docs = self.booleanRetrieve(query)
		if len(query) == 1:
			docs.sort()
			return docs

		validDocs = []
		validDocPostings = {} # {docId: [postings]}

		for queryIndex in range(len(query)):
			validDocs = list(docs)
			docs = []
			posting1 = []
			posting2 = []

			for validDocIndex in range(len(validDocs)):
				docId = validDocs[validDocIndex]
				if validDocIndex == 0:
					validDocPostings[docId] = self.invertedIndex[query[0]][docId]
					docs.append(docId)
					continue
				posting1 = validDocPostings[docId]
				posting2 = self.invertedIndex[query[queryIndex]][docId]
				newValidPostings = []
				postingIndex1 = 0
				postingIndex2 = 0

				posting1.sort()
				posting2.sort()


				while postingIndex1 != len(posting1) and postingIndex2 != len(posting2):
					posting1Pos = posting1[postingIndex1]
					posting2Pos = posting2[postingIndex2]
					if posting1Pos < posting2Pos:
						if posting1Pos + 1 == posting2Pos:
							docs.append(docId)
							newValidPostings.append(posting2Pos)
						postingIndex1 += 1
					else:
						postingIndex2 += 1

				validDocPostings[docId] = newValidPostings

		docs.sort()
		return docs

	def rankRetrieve(self, query):
		scores = [0.0 for _ in range(len(self.documents))]
		length = [0.0 for _ in range(len(self.documents))]

		# Cosine similarity
		for term in query:
			weightTermQuery = 1 + math.log(query.count(term), 10)
			docsWithWord = self.getPosting(term)
			for docId in docsWithWord:
				scores[int(docId)] = weightTermQuery * self.getTFIDF(term, str(docId))

		for docId in range(len(scores)):
			for word in self.documents[str(docId)]:
				length[docId] +=  math.pow(self.getTFIDF(word, str(docId)), 2)
			length[docId] = math.sqrt(length[docId])

		for docId in range(len(scores)):
			if length[docId] != 0:
				scores[docId] = scores[docId] / length[docId]

		pQueue = Queue.PriorityQueue()
		for docId in range(len(scores)):
			pQueue.put((-scores[docId], docId))

		top5 = []

		for _ in range(3):
			if not pQueue.empty():
				top5.append(pQueue.get())
		return top5


	def loadData(self):
		"""
		Loads precomputed values if available.
		If no precomputed data then it computes and stores the results
		"""
		if self.precomputedDataExists():
			self.loadPrecomputedData()
		else:
			self.computeAndStoreData()

	def precomputedDataExists(self):
		precomputationPath = "computations/"
		if os.listdir(precomputationPath) == []:
			return False
		else:
			return True


	def loadPrecomputedData(self):
		print "Loading precomputed data ...." 

		# vocabulary
		vocabularyPath = "computations/vocabulary.json"
		file = open(vocabularyPath, "r")
		self.vocabulary = json.loads(file.read())
		file.close()

		# inverted-index
		invertedIndexPath = "computations/invertedIndex.json"
		file = open(invertedIndexPath, "r")
		self.invertedIndex = json.loads(file.read())
		file.close()

		# tfidf
		tfidfPath = "computations/tfidf.json"
		file = open(tfidfPath, "r")
		self.tfidf = json.loads(file.read())
		file.close()

		# docIdToFilename
		docIdToFilenamePath = "computations/docIdToFilename.json"
		file = open(docIdToFilenamePath, "r")
		self.docIdToFilename = json.loads(file.read())
		file.close()

		#documents
		documentsPath = "computations/documents.json"
		file = open(documentsPath, "r")
		self.documents = json.loads(file.read())
		file.close()

		#documents
		documentsPath = "computations/documentsUnstemmed.json"
		file = open(documentsPath, "r")
		self.documents = json.loads(file.read())
		file.close()

		#stop words
		stopPath = "computations/stop.json"
		file = open(stopPath, "r")
		self.stopWords = json.loads(self.stopWords)
		file.close()

		print "Finished loading precomputed data ...." 




	def computeAndStoreData(self):
		print "Compute and store data ...."
		self.readData2("crawler/data/")
		self.index()
		self.computeTFIDF()

		# vocabulary
		vocabularyPath = "computations/vocabulary.json"
		file = open(vocabularyPath, "w")
		file.write(json.dumps(self.vocabulary))
		file.close()

		# inverted-index
		invertedIndexPath = "computations/invertedIndex.json"
		file = open(invertedIndexPath, "w")
		file.write(json.dumps(self.invertedIndex))
		file.close()

		# tfidf
		tfidfPath = "computations/tfidf.json"
		file = open(tfidfPath, "w")
		file.write(json.dumps(self.tfidf))
		file.close()

		# docIdToFilename
		docIdToFilenamePath = "computations/docIdToFilename.json"
		file = open(docIdToFilenamePath, "w")
		file.write(json.dumps(self.docIdToFilename))
		file.close()

		#documents
		documentsPath = "computations/documents.json"
		file = open(documentsPath, "w")
		file.write(json.dumps(self.documents))
		file.close()

		#documents
		documentsPath = "computations/documentsUnstemmed.json"
		file = open(documentsPath, "w")
		file.write(json.dumps(self.documents))
		file.close()

		#stop words
		stopPath = "computations/stop.json"
		file = open(stopPath, "w")
		file.write(json.dumps(self.stopWords))
		file.close()

		print "Finished Computing and storing data ...."

	def findRelevantLines(self, query):
		relevantLines = ""
		query = query.lower()
		query = query.split()
		query = [self.stemmer.stem(word) for word in query]
		query = self.removeStopWords(query)
		docScores = self.rankRetrieve(query)
		if docScores == []:
			return "I have no such information, but I am learning."

		for docScore in docScores:
			(_, bestDocId) = docScore
			line = self.documentsUnstemmed[str(bestDocId)]
			line = "-> " + " ".join(line) + ".\n"
			relevantLines += line

		return relevantLines

	def removeStopWords(self, words):
		result = [word for word in words if word not in self.stopWords]
		return results

def testRetrival():
	brain = BotBrain()
	brain.loadData()
	print brain.findRelevantLines("tell me history")

if __name__ == '__main__':
	testRetrival()






































