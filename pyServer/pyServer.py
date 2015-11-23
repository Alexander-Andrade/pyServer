﻿import sys  #for IP and port passing
import socket
import re   #regular expressions
from Connection import Connection
from FileWorker import FileWorkerError
from SocketWrapper import*
import time
import multiprocessing
import types

class TCPServer(Connection):


    def __init__(self, IP,port,nConnections = 1,sendBuflen = 2048,timeOut = 60):

        super().__init__(sendBuflen,timeOut)
        self.servSock = TCP_ServSockWrapper(IP,port,nConnections) 
       
        self.__fillCommandDict()
        self.clientsId = []

    def __fillCommandDict(self):
        self.commands.update({'echo':self.echo,
                              'time':self.time,
                              'quit':self.quit,
                              'download':self.sendFileTCP,
                              'upload':self.recvFileTCP})
       

    def echo(self,commandArgs):
        self.talksock.sendMsg(commandArgs)


    def time(self,commandArgs):
        self.talksock.sendMsg(time.asctime())

    def quit(self,commandArgs):
        self.talksock.raw_sock.shutdown(socket.SHUT_RD)
        self.talksock.raw_sock.close()


    def sendFileTCP(self,commandArgs):
        self.sendfile(self.talksock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file downloaded")


    def recvFileTCP(self,commandArgs):
        self.receivefile(self.talksock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file uploaded")


    def recoverTCP(self,timeOut):
        self.servSock.settimeout(timeOut)
        try:
            self.__registerNewClient()
        except TimeoutError:
            raise FileWorkerError("fail to reconnect")
        #compare prev and cur clients id's, may be the same client
        if self.clientsId[0] != self.clientsId[1]:
            raise FileWorkerError("new client has connected")
        return self.talksock


    def recowerUdp():
        pass

    def __clientCommandsHandling(self):
        while True:
            try:
                message = self.talksock.recvMsg()
                if len(message) == 0:
                    break
                regExp = re.compile("[A-Za-z0-9_]+ *.*")
                if regExp.match(message) is None:
                    self.talksock.sendMsg("invalid command format \"" + message + "\"")
                    continue
                if not self.catchCommand(message):
                    self.talksock.sendMsg("unknown command")
                #quit
                if message.find("quit") != -1:
                    break
            except FileWorkerError as e:
                #file transfer exception
                print(e.args[0])
            except OSError:
                #we can't crash the server
                pass 


    def writeClientId(self,id):
        if len(self.clientsId) == 2:
            #pop old id
            self.clientsId.pop(0)
        #write new id
        self.clientsId.append(id)
            
                    
    def __registerNewClient(self):
        sock, addr = self.servSock.raw_sock.accept()
        self.talksock = SockWrapper(raw_sock=sock,inetAddr=addr)
        #get id from client
        id = self.talksock.recvInt()
        self.writeClientId(id)

    def workWithClients(self):
        while True:
            self.__registerNewClient()
            self.__clientCommandsHandling()
    
   
if __name__ == "__main__":
    
    server = TCPServer(None,sys.argv[1])
    server.workWithClients()
    