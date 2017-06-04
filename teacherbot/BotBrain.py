
class BotBrain:
	def __init__(self):
		self.vocabulary = []
		self.invertedIndex = {} 
		self.documents = []

	def readData(self):
		return []

	def computeTFIDF(self):
		print "Computing tfidf..."

		tfidf = {} # {word: { docId: tfidf}}
		for docId, document in enumerate(self.documents):
			for word in document:
				wordCountInDocument = len(invertedIndex[word][docId])
				if word not in tfidf.keys():
					tfidf[word] = {}
				if docId not in tfidf[word].keys():
					tfidf[word][docId] = 0
				tfidf[word][docId] += wordCountInDocument

		for word in tfidf.keys():
			documentsWithWord = tfidf[word].keys()
			idf = math.log(len(documents), 10) / len(docsWithWord)
			for docId in docsWithWord:
				tf = 1 + math.log(tfidf[word][docId], 10)
				tfidf[word][docId] = tf * idf


	def getTFIDF(self, word, documentId):
		if not tfidf[word][documentId]:
			return 0.0

		return tfidf[word][documentId]

	def index(self):
		print "starting indexing..."

		# Populating invertedIndex  { word : { docId: [positions]}}
		for word in self.vocabulary:
			invertedIndex[word] = {}

		for docId, document in enumerate(self.documemts):
			for wordIndex, word in enumerate(document):
				if wordIndex not in self.invertedIndex[word].keys():
					self.invertedIndex[word][docId] = []
				self.invertedIndex[word][docId].append(wordIndex)

		# Creating doc id to doc words map {docId: set(docWords)}
		idToDocWords = {}
		for docId, document in enumerate(self.documents):
			idToDocWords[docId] = set(document)
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
		docs = getPosting(query[0])
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
			posting2 = getPosting(query[queryIndex])
			postingIndex1 = 0
			postingIndex2 = 0

			if len(posting1) == 0 || len(posting2) == 0:
				return []

			posting1.sort()
			posting2.sort()

			while postingIndex1 != len(posting1) && postingIndex2 != len(posting2):
				posting1DocId = posting1[postingIndex1]
				posting2DocId = posting2[postingIndex2]
				if posting1DocId == posting2DocId:
					docs.extend(posting1DocId)
					postingIndex1 += 1
					postingIndex2 += 1
				elif posting1DocId < posting2DocId:
					postingIndex1 += 1
				else:
					postingIndex2 += 1


			docs.sort()
			return docs

	def phraseRetrieve(self, query)
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


				while postingIndex1 != len(posting1) && postingIndex2 != len(posting2):
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
		scores = [None for _ in range(len(self.documemts))]
		length = [None for _ in range(len(self.documemts))]

		# Cosine similarity
		for term in query:
			weightTermQuery = 1 + math.log(query.count(term), 10)
			docsWithWord = self.getPosting(term)
			for docId in docsWithWord:
				scores[docId] = weightTermQuery * getTFIDF(term, docId)

		for docId in range(len(scores)):
			for word in self.documents[docId]:
				length[docId] +=  math.pow(self.getTFIDF(word, docId), 2)
			length[docId] = math.sqrt(length[docId])

		for docId in range(len(scores)):
			if length[docId] != 0:
				scores[docId] = scores[docId] / length[docId]


		pQueue = Queue.PriorityQueue()
		for docId in range(len(scores)):
			pq.put((docId, scores[docId]))

		top5 = []

		for _ in range(5):
			if not pQueue.empty():
				top5.append(pQueue.get())

		return top5


def test():
	






































