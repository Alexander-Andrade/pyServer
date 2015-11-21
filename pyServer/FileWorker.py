from SocketWrapper import SocketWrapper
import sys
class FileWorkerError(Exception):
    #
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class FileWorker:
    
    def __init__(self,sockWrapper,recoveryFunc,bufferSize,timeOut):
        self.timeOut = timeOut
        self.bufferSize = bufferSize
        self.sock = sockWrapper
        self.fileLen = 0
        self.filePos = 0
        self.loadingPercent = 0
        #UDP packet controll
        self.datagramsId = []
        #number of udp datagrams answer send afrer
        self.nUdpPacksCtrl = 1
        self.recoveryFunc = recoveryFunc

    def getFileLength(self):
        #to the file end
        self.file.seek(0,2)
        size = self.file.tell()
        self.file.seek(0)
        return size
    
    def outFileInfo(self):
        #print file name
        print("filename:",end='')
        print(self.fileName)
        #file size
        print("file size:",end='')
        print(self.fileLen,flush=True)

    def send(self,fileName):
        self.fileName = fileName
        
        try:
            #binary mode
            self.file = open(fileName,'rb')
        except OSError:
            #say to receiver that can't open the file
            self.sock.sendRefuse()
            raise FileWorkerError("can't open the file")
        self.sock.sendConfirm()

        self.sock.setSendBufferSize(self.bufferSize)
        #real system buffer size can differ
        self.bufferSize = self.sock.getSendBufferSize()
        self.fileLen = self.getFileLength()
        #send hint data to the receiver
        try:
            self.sock.sendNum(self.bufferSize)
            self.sock.sendNum(self.timeOut)
            self.sock.sendNum(self.fileLen)
        except OSError:
            raise FileWorkerError("can't send file metadata")
        self.outFileInfo
        #file transfer
        try:
            while True:
                data = self.file.read(self.bufferSize)
               
                #eof check
                if not data:
                    self.sock.raw_sock.settimeout(self.timeOut)
                    #receiver acknowledge received data size
                    receiverPos = self.sock.recvNum()
                    if receiverPos == self.filePos:
                        break
                    else:
                        raise OSError("fail to transfer file")
                    
                self.sock.raw_sock(data)
                self.filePos += len(data)

        except OSError as e:
            #file transfer reconnection
            print(ellipsis.args[0])
        finally:
            self.file.close() 



