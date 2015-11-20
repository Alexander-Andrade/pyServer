﻿import sys  #for IP and port passing
import socket
import re   #regular expressions
from Connection import*


class TCPServer(Connection):


    def __init__(self, IP,port,nConnections = 1,sendBuflen = 2048,timeOut = 30):

        super().__init__(sendBuflen,timeOut)
        self.IP = IP
        self.port = port
        self.__createServer(IP,port,nConnections)


    def __createServer(self, IP,port,nConnections = 1):
       
        #  getaddrinfo returns a list of 5-tuples with the following structure(family, type, proto, canonname, sockaddr)
        for addrInfo in socket.getaddrinfo(self.IP,self.port,socket.AF_INET,
                                           socket.SOCK_STREAM,socket.IPPROTO_TCP,socket.AI_PASSIVE):
            af_family,socktype,proto,canonname,sockaddr = addrInfo

            try:
                self.servSock = socket.socket(af_family,socktype,proto)
                
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

    
    def __acceptNewClient(self):

        """conn is a new socket object usable to send and receive data
        on the connection, and address is the address bound to the socket
        on the other end of the connection.
        """
        self.contactSock,self.curClientAddr = self.servSock.accept()
      

    def __clientCommandsHandling(self):

        while True:
            message = self.contactSock.recv()
            if len(message) == 0:
                break
            
            regExp = re.compile("( )*[A-Za-z0-9]+(( )+(.)+)?(\r\n|\n)")
            if not regExp.match(message):
                self.contactSock.sendMsg("invalid command format \"" + message)
                continue

            self.contactSock.sendMsg("abra cadabra");


    def workWithClients(self):

        while True:
            self.__acceptNewClient()
            self.__clientCommandsHandling()
    
      
       
        

if __name__ == "__main__":
    

    server = TCPServer(sys.argv[1],sys.argv[2])
    server.workWithClients()
    