
import cmd

from TeacherBot import TeacherBot

class BotCmd(cmd.Cmd):
    
    teacherBot = TeacherBot()

    def cmdloop(self, intro=None):
        return cmd.Cmd.cmdloop(self, intro)

    # def preloop(self):

    # def postloop(self):   

    def onecmd(self, str):
        cmd.Cmd.onecmd(self, str)

    def emptyline(self):
        return cmd.Cmd.emptyline(self)

    def default(self, line):
        if line == 'q':
            return True
        else:
            print 'Bot: ' + self.teacherBot.getResponse(line)

    def postcmd(self, stop, line):
        if line == 'q':
            return True

if __name__ == '__main__':
    botCmd = BotCmd()
    botCmd.prompt = "You: "
    botCmd.cmdloop(intro="Eric")

