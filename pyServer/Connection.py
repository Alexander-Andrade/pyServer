import sys
from random import randint
import re

class Connection:
    
    def __init__(self,sendBufLen,timeOut):
        
        self.id = randint(0,sys.maxsize - 1)  
        self.sendBufLen = sendBufLen
        self.timeOut = timeOut
        self.commands = dict()


    def recvMsg(self,sock):
        # first byte = message length
        length = sock.recv(1) 
        return  sock.recv(length)

    def sendMsg(self,sock,msg):
        #send length first
        sock.send(len(msg))
        sock.sendall(msg)

    def recvall(self,sock,length):
       total = 0
       data = b""
       while(total < n):
           data += sock.recv(length - total)
           total += len(data)
       return data 

    def checkCommandExistance(self,command):
        return command in self.commands

    def catchCommand(self,commandMsg):
       commandRegEx = re.compile("[A-Za-z0-9_]+")
       #match() Determine if the RE matches at the beginning of the string.
       matchObj = commandRegEx.match(commandMsg)
       if(matchObj == None):
           #there is no suitable command
           return False
       #group()	Return the string matched by the RE
       command = matchObj.group()
       #end()	Return the ending position of the match
       commandEndPos = matchObj.end()
       #cut finding command from the commandMes
       request = commandMsg[commandEndPos:]

       if(checkCommandExistance(command) == True):
           self.commands[command](request)
    
