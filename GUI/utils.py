import socket
import pickle
import struct

def send(channel, *args):
    buffer = pickle.dumps(args)
    value = socket.htonl(len(buffer))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buffer)

def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error as e:
        return ''
    buf = ""
    while len(buf) < size:
        buf = channel.recv(size - len(buf))
    return pickle.loads(buf)[0]

def sendClientList(channel, listDict):
    data = {}
    for clientSocket in listDict.keys():
        tempData = listDict[clientSocket]
        data[tempData[0]] = tempData[1]
    dataToSend = {"clientList":data}
    send(channel,dataToSend)
    
def receiverClientList(channel):
    return receive(channel)

def sendGroupList(channel, groupDict):
    data = {"groupList":groupDict}
    send(channel,data)

def sendMessage(channel, message):
    data = {"message":message}
    send(channel,data)

def sendGroupMessage(channel, message):
    data = {"groupMessage":message}
    send(channel,data)

def sendCreateRoomRequest(channel, message):
    data = {"requestCreateRoom": message}
    send(channel,data)

def sendJoinRoomRequest(channel, message):
    data = {"requestJoinRoom":message}
    send(channel,data)