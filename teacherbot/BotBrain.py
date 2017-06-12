
from __future__ import division
import math
import Queue
import os
import json

class BotBrain:
	def __init__(self):
		self.vocabulary = []
		self.invertedIndex = {} 
		self.documents = []
		self.tfidf = {} # {word: { docId: tfidf}}
		self.docIdToFilename = {}


	def readData(self, dataDirectory):
		filenames = []
		for filename in os.listdir(dataDirectory):
			if filename.endswith("txt") and not filename.startswith("."):
				filenames.append(filename)
				print filename

		filenames = filenames[:5]

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


	"""
		Call after indexing
	"""
	def computeTFIDF(self):
		print "Computing tfidf..."

		for docId in self.documents.keys():
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
			idToDocWords[str(docId)] = set(document)
		self.documents = idToDocWords

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
			pQueue.put((scores[docId], docId))

		top5 = []

		for _ in range(5):
			if not pQueue.empty():
				top5.append(pQueue.get())
		top5.reverse()		
		return top5


	def loadData(self):
		"""
		Loads precomputed values if available.
		If no precomputed data then it computes and stores the results
		"""
		if self.precomputedDataExists():
			self.loadPrecomputedData()
		else:
			self.computedAndStoreData()

	def precomputedDataExists(self):
		precomputationPath = "computations/"
		if os.listdir(precomputationPath) == []:
			return False
		else:
			return True


	def loadPrecomputedData(self):
		return

	def computeAndStoreData(self):
		self.readData("crawler/data/")
		self.index()
		self.computeTFIDF()

		# vocabulary
		vocabularyPath = "computations/vocabulary"
		file = open(vocabularyPath, "w")
		file.write(json.dumps(self.vocabulary))
		file.close()

		# inverted-index
		invertedIndexPath = "computations/invertedIndex"
		file = open(invertedIndexPath, "w")
		file.write(json.dumps(self.invertedIndex))
		file.close()

		# tfidf
		tfidfPath = "computations/tfidf"
		file = open(tfidfPath, "w")
		file.write(json.dumps(self.tfidf))
		file.close()

		# docIdToFilename
		docIdToFilenamePath = "computations/docIdToFilename"
		file = open(docIdToFilenamePath, "w")
		file.write(json.dumps(self.docIdToFilename))
		file.close()


def testRetrival():
	brain = BotBrain()
	# brain.readData("crawler/data/")
	# brain.index()
	# brain.computeTFIDF()
	# print brain.rankRetrieve("History is the discovery, collection, organization, analysis, and presentation of information about past events. History ".split())
	# print brain.precomputedDataExists()
	brain.computeAndStoreData()

if __name__ == '__main__':
	testRetrival()






































