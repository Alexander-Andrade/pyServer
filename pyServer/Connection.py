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
        length = int.from_bytes(sock.recv(1),byteorder='big') 
        return  sock.recv(length).decode('utf-8')

    def sendMsg(self,sock,msg):
        #send length first
        sock.send(len(msg).to_bytes(1,byteorder='big'))
        sock.sendall(msg.encode('utf-8'))

    def sendNum(self,sock,n):
        sock.send(n.to_bytes(4,byteorder='big'))

    def recvNum(self,sock):
        return int.from_bytes(sock.recv(4),byteorder='big')

    def recvall(self,sock,length):
       total = 0
       data = None
       while(total < n):
           data += sock.recv(length - total)
           total += len(data)
       return data 


    def catchCommand(self,commandMsg):
       commandRegEx = re.compile("[A-Za-z0-9_]+")
       #match() Determine if the RE matches at the beginning of the string.
       matchObj = commandRegEx.match(commandMsg)
       if(matchObj == None):
           #there is no suitable command
           return False
       #group()	Return the string matched by the RE
       command = matchObj.group()
       if command in self.commands:
           #end() Return the ending position of the match
           commandEndPos = matchObj.end()
           #cut finding command from the commandMes
           request = commandMsg[commandEndPos:]
           #cut spaces after command
           request.lstrip()
           self.commands[command](request)
           return True
       return False 
