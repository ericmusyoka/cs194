import aiml

class TeacherBot:
	def __init__(self):
		self.templateHandler = aiml.Kernel()
		self.templateHandler.learn('template.xml')

	def getResponse(self, line):
		return self.templateHandler.respond(line)

if __name__ == '__main__':
	TeacherBot()

