import aiml

from BotBrain import BotBrain

class TeacherBot:
	def __init__(self):
		self.templateHandler = aiml.Kernel()
		self.templateHandler.learn('template.xml')
		self.templateHandler.verbose(isVerbose=False)
		self.initBrain()


	def initBrain(self):
		self.brain = BotBrain()
		self.brain.loadData()

	def getResponse(self, line):
		response = self.templateHandler.respond(line)
		if response == "":
			return str(self.brain.rankRetrieve(line))
		else:
			return response


if __name__ == '__main__':
	TeacherBot()

