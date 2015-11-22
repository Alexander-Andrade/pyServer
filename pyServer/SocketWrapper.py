from socket import*
import struct

class SocketWrapper:

    def __init__(self,**sockArgs):
        self.raw_sock = sockArgs.get('raw_sock')
        self.addr_info = sockArgs.get('addr_info')
   
    def recvMsg(self):
        # first byte = message length
        length = int.from_bytes(self.raw_sock.recv(1),byteorder='big') 
        return  self.raw_sock.recv(length).decode('utf-8')

    def sendMsg(self,msg):
        #send length first
        self.raw_sock.send(len(msg).to_bytes(1,byteorder='big'))
        self.raw_sock.sendall(msg.encode('utf-8'))

    def sendInt(self,n):
        self.raw_sock.send(n.to_bytes(4,byteorder='big'))

    def recvInt(self):
        return int.from_bytes(self.raw_sock.recv(4),byteorder='big')

    def recvall(self,length):
       total = 0
       data = None
       while(total < n):
           data += self.raw_sock.recv(length - total)
           total += len(data)
       return data

    def sendConfirm(self):
        return self.sendInt(1)

    def sendRefuse(self):
        return self.sendInt(0)

    def recvAck(self):
        return True if self.recvInt() == 1 else False

    def setSendBufferSize(self,value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDBUF, value)

    def setReceiveBufferSize(self,value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVBUF,value)

    def getSendBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_SNDBUF)

    def getReceiveBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_RCVBUF)
    
    def setSendTimeout(self,timeOutSec):
        timeval = struct.pack("2I",timeOutSec,0)
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO, timeval )

    def disableSendTimeout(self):
        timeval = struct.pack("2I",0,0)
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timeval)

    def setReceiveTimeout(self,timeOutSec):
        timeval = struct.pack("2I",timeOutSec,0)
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timeval)

    def disableReceiveTimeout(self):
        timeval = struct.pack("2I",0,0)
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO, timeval)