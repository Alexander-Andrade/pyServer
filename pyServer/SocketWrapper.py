from socket import*

class SocketWrapper:

    def __init__(self, sock):
        self.raw_sock = sock
   
    def recvMsg(self):
        # first byte = message length
        length = int.from_bytes(self.raw_sock.recv(1),byteorder='big') 
        return  self.raw_sock.recv(length).decode('utf-8')

    def sendMsg(self,msg):
        #send length first
        self.raw_sock.send(len(msg).to_bytes(1,byteorder='big'))
        self.raw_sock.sendall(msg.encode('utf-8'))

    def sendNum(self,n):
        self.raw_sock.send(n.to_bytes(4,byteorder='big'))

    def recvNum(self):
        return int.from_bytes(self.raw_sock.recv(4),byteorder='big')

    def recvall(self,length):
       total = 0
       data = None
       while(total < n):
           data += self.raw_sock.recv(length - total)
           total += len(data)
       return data

    def sendConfirm(self):
        return self.sendNum(1)

    def sendRefuse(self):
        return self.sendNum(0)

    def revcAck(self):
        return True if self.recvNum() == 1 else False

    def setSendBufferSize(self,value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDBUF, value)

    def setReceiveBufferSize(self,value):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVBUF,value)

    def getSendBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_SNDBUF)

    def getReceiveBufferSize(self):
        return self.raw_sock.getsockopt(SOL_SOCKET, SO_RCVBUF)
    
    def setSendTimeout(self,timeOutSec):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO, timeOutSec)

    def disableSendTimeout(self):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO,0)

    def setReceiveTimeout(self,timeOutSec):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timeOutSec)

    def disableReceiveTimeout(self):
        self.raw_sock.setsockopt(SOL_SOCKET, SO_SNDTIMEO,0)