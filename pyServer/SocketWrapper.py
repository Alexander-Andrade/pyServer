﻿from socket import*
import struct
import sys
from random import randint

class SockWrapper:

    def __init__(self,**sockArgs):
        self.raw_sock = sockArgs.get('raw_sock')
        self.inetAddr = sockArgs.get('inetAddr')
        self.family = sockArgs.get('family',AF_UNSPEC)
        self.type = sockArgs.get('type',SOCK_STREAM)
        self.proto = sockArgs.get('proto',IPPROTO_TCP)
        self.id = randint(0,65534) if sockArgs.get('createId') else None
   
    def attachServToAddr(self,addrInfo):
        af_family,socktype,sock,canonname,sockaddr = addrInfo
        try:
            self.raw_sock = socket(af_family,socktype,sock)
            """All errors raise exceptions. The normal exceptions for invalid argument
            types and out-of-memory conditions can be raised; starting from Python 3.3,
            errors related to socket or address semantics raise OSError or one of its
            subclasses (they used to raise socket.error).
            """
        except OSError as msg:
            self.raw_sock = None
            return False                   
        try:
            self.raw_sock.bind(sockaddr)
        except OSError as msg:
            self.raw_sock.close()
            self.raw_sock = None
            return False
        return True          

    def _attachServSock(self):
        #  getaddrinfo returns a list of 5-tuples with the following structure(family, type, sock, canonname, sockaddr)
        for self.addr_info in getaddrinfo(self.inetAddr[0],self.inetAddr[1],self.family,
                                           self.type,self.proto,AI_PASSIVE):
            if self.attachServToAddr(self.addr_info):
                break
        if self.raw_sock is None:
            raise OSError("can't create server")
            

    def attachClientToAddr(self,addrInfo):
        af_family,socktype,proto,canonname,sockaddr = addrInfo
        try:
            self.raw_sock = socket(af_family,socktype,proto)
        except OSError as msg:
            self.raw_sock = None
            return False
        if self.proto == IPPROTO_TCP:
            try:
                self.raw_sock.connect(sockaddr)
            except OSError as msg:
                self.raw_sock.close()
                self.raw_sock = None
                return False
            return True

    def _attachClientSock(self):
        for self.addr_info in getaddrinfo(self.inetAddr[0],self.inetAddr[1],self.family,self.type,self.proto):
            if self.attachClientToAddr(self.addr_info):
                break
        if self.raw_sock is None:
            raise OSError("fail to connect to the socket")
             
    
    def reattachClientSock(self):
        if self.raw_sock is not None:
            self.raw_sock.close()
            self.raw_sock = None
        return self.attachClientToAddr(self.addr_info)

    def send(self,data,flags=0):
        return self.raw_sock.send(data, flags)

    def sendall(self,data):
        return self.raw_sock.sendall(data)

    def recv(self,size,flags=0):
        return self.raw_sock.recv(size, flags)

    def recvMsg(self):
        # first byte = message length
        length = int.from_bytes(self.recv(1), byteorder='big')
        return  self.recv(length).decode('utf-8')

    def sendMsg(self,msg):
        #send length first
        self.send(len(msg).to_bytes(1, byteorder='big'))
        self.sendall(msg.encode('utf-8'))

    def sendInt(self,n,size=4):
        self.send(n.to_bytes(size, byteorder='big'))

    def recvInt(self,size=4):
        return int.from_bytes(self.recv(size), byteorder='big')

    def receive(self,length,flags=0):
       total = 0
       data = b''
       while(total < length):
           data += self.recv(length - total,flags)
           total += len(data)
       return data

    def sendConfirm(self):
        return self.sendInt(1)

    def sendRefuse(self):
        return self.sendInt(0)

    def recvAck(self):
        return True if self.recvInt() == 1 else False

    def setSendBufferSize(self, value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDBUF, value)

    def setReceiveBufferSize(self, value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVBUF,value)

    def getSendBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_SNDBUF)

    def getReceiveBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_RCVBUF)
    
    def setSendTimeout(self,timeOutSec):
        if sys.platform.startswith('win'):
            timeval = timeOutSec * 1000
        elif sys.platform.startswith('linux'):
            self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO, struct.pack("LL", timeOutSec, 0))

    def disableSendTimeout(self):
        if sys.platform.startswith('win'):
            timeval = 0
        elif sys.platform.startswith('linux'):
            self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO, struct.pack("LL",0,0))

    def setReceiveTimeout(self,timeOutSec):
        if sys.platform.startswith('win'):
            timeval = timeOutSec * 1000
        elif sys.platform.startswith('linux'):
            self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack("LL", timeOutSec, 0))

    def disableReceiveTimeout(self):
        if sys.platform.startswith('win'):
            timeval = 0
        elif sys.platform.startswith('linux'):
            self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack("LL",0,0))



class TCP_ServSockWrapper(SockWrapper):

    def __init__(self, IP, port, nConnections=1,**sockArgs):
        super().__init__(inetAddr=(IP, port),**sockArgs)
        self.nConnections = nConnections  
        self._attachServSock()
        self.raw_sock.listen(self.nConnections)

    
class UDP_ServSockWrapper(SockWrapper):

    def __init__(self, IP, port,**sockArgs):
        super().__init__(inetAddr=(IP, port), type=SOCK_DGRAM,proto=IPPROTO_UDP,**sockArgs)
        self._attachServSock()
        self.clientAddr = None

    def recv(self,size,flags=0):
        data,self.clientAddr = self.raw_sock.recvfrom(size,flags)
        return data

    def send(self,data,flags=0):
        return self.raw_sock.sendto(data,flags,self.clientAddr)



class TCP_ClientSockWrapper(SockWrapper):
    
    def __init__(self, IP, port,**sockArgs):
        super().__init__(inetAddr=(IP, port),**sockArgs)
        self._attachClientSock()

class UDP_ClientSockWrapper(SockWrapper):

    def __init__(self, IP, port,**sockArgs):
        super().__init__(inetAddr=(IP, port), type=SOCK_DGRAM,proto=IPPROTO_UDP,**sockArgs)
        self._attachClientSock()

    def send(self,data,flags=0):
        return self.raw_sock.sendto(data,flags,self.addr_info[4])

    def recv(self,size,flags=0):
        data,servAddr = self.raw_sock.recvfrom(size,flags)
        return data