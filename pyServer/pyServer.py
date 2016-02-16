import sys  #for IP and port passing
import socket
import re   #regular expressions
from Connection import Connection
from FileWorker import*
from SocketWrapper import*
import time
import multiprocessing as mp


class TCPServer(Connection):


    def __init__(self, IP,port,nConnections = 1,sendBuflen = 1024,timeOut = 15):
        super().__init__(sendBuflen,timeOut)
        self.servSock = TCP_ServSockWrapper(IP,port,nConnections) 
        self.talksock = None
        self.udpServSock = UDP_ServSockWrapper(IP,port)
        self.__fillCommandDict()

    def __fillCommandDict(self):
        self.commands.update({'echo':self.echo,
                              'time':self.time,
                              'quit':self.quit,
                              'download':self.sendFileTCP,
                              'upload':self.recvFileTCP,
                              'download_udp':self.sendFileUDP,
                              'upload_udp': self.recvFileUDP})
       

    def echo(self,commandArgs):
        self.talksock.sendMsg(commandArgs)


    def time(self,commandArgs):
        self.talksock.sendMsg(time.asctime())

    def quit(self,commandArgs):
        self.talksock.raw_sock.shutdown(SHUT_RDWR)
        self.talksock.raw_sock.close()
        self.talksock.raw_sock = None


    def sendFileTCP(self,commandArgs):
        self.sendfile(self.talksock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file downloaded")


    def recvFileTCP(self,commandArgs):
        self.receivefile(self.talksock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file uploaded")


    def recoverTCP(self,timeOut):
        self.servSock.raw_sock.settimeout(timeOut)
        prevClientId = self.talksock.id
        try:
            self.__registerNewClient()
        except OSError as e:
            #disable timeout
            self.servSock.raw_sock.settimeout(None)
            raise 
        #compare prev and cur clients id's, may be the same client
        if self.talksock.id != prevClientId:
            raise OSError("new client has connected")
        return self.talksock


    def sendFileUDP(self,commandArgs):
        #get cur client addr
        self.udpServSock.recvInt()
        self.sendfile(self.udpServSock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file downloaded")

    def recvFileUDP(self,commandArgs):
        #get cur client addr
        self.udpServSock.recvInt()
        self.receivefile(self.udpServSock,commandArgs,self.recoverTCP)
        self.talksock.sendMsg("file uploaded")

    def recowerUdp():
        pass

    def __clientCommandsHandling(self):
        while True:
            try:
                message = self.talksock.recvMsg()
                if not message:
                    self.talksock.sendMsg('empty command')
                    continue
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
                #can work with the same client
                print(e)
                
            except (OSError,FileWorkerCritError):
                #wait for the new client
                break
            
                             
    def __registerNewClient(self):
        sock, addr = self.servSock.raw_sock.accept()
        self.talksock = SockWrapper(raw_sock=sock,inetAddr=addr)
        #get id from client
        self.talksock.id = self.talksock.recvInt()

    def workWithClients(self):
        while True:
            self.__registerNewClient()
            self.__clientCommandsHandling()
    
   
if __name__ == "__main__":
    
    server = TCPServer("192.168.1.2","6000")
    server.workWithClients()
    