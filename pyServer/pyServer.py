import sys  #for IP and port passing
import socket
import re   #regular expressions
from Connection import*
import datetime
import multiprocessing
import types

class TCPServer(Connection):


    def __init__(self, IP,port,nConnections = 1,sendBuflen = 2048,timeOut = 30):

        super().__init__(sendBuflen,timeOut)
        self.IP = IP
        self.port = port
        self.__createServer(IP,port,nConnections)
        self.__fillCommandDict()
        self.clientsId = []

    def __fillCommandDict(self):
        self.commands.update({'echo':self.echo,
                              'time':self.time,
                              'quit':self.quit,
                              'download':self.sendFile,
                              'upload':self.recvFile})
       

    def __createServer(self, IP,port,nConnections = 1):
        #  getaddrinfo returns a list of 5-tuples with the following structure(family, type, sock, canonname, sockaddr)
        for addrInfo in socket.getaddrinfo(self.IP,self.port,socket.AF_INET,
                                           socket.SOCK_STREAM,socket.IPsock_TCP,socket.AI_PASSIVE):
            af_family,socktype,sock,canonname,sockaddr = addrInfo
            try:
                self.servSock = socket.socket(af_family,socktype,sock)
                
                """All errors raise exceptions. The normal exceptions for invalid argument
                types and out-of-memory conditions can be raised; starting from Python 3.3,
                errors related to socket or address semantics raise OSError or one of its
                subclasses (they used to raise socket.error).
                """
            except OSError as msg:
                self.servSock = None
                continue                   
            try:
                self.servSock.bind(sockaddr)
                self.servSock.listen(nConnections)
            except OSError as msg:
                self.servSock.close()
                self.servSock = None
                continue
            
            break
        if self.servSock is None:
            print("can't create server")
            sys.exit(1)


    def echo(self,commandArgs):
        self.talksock.sendMsg(self.contactSock,commandArgs)


    def time(self,commandArgs):
        self.talksock.sendMsg(self.contactSock, str(datetime.datetime.now()) )

    def quit(self,commandArgs):
        self.talksock.raw_sock.shutdown(socket.SHUT_RD)
        self.talksock.raw_sock.close()


    def sendFile(self,commandArgs):
        pass


    def recvFile(self,commandArgs):
        pass


    def __clientCommandsHandling(self):
        while True:
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


    def writeClientId(self,id):
        if len(self.clientsId) == 2:
            #pop old id
            self.clientsId.pop(0)
        #write new id
        self.clientsId.append(id)
            
                    
    def __registerNewClient(self):
        contactSock,self.curClientAddr = self.servSock.accept()
        self.talksock = SocketWrapper(contactSock)
        #get id from client
        id = self.talksock.recvNum()
        self.writeClientId(id)

    def workWithClients(self):
        while True:
            self.__registerNewClient()
            self.__clientCommandsHandling()
    
   
if __name__ == "__main__":
    
    server = TCPServer(None,sys.argv[1])
    server.workWithClients()
    