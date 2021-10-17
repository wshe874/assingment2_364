import select
import socket
import sys
import signal
import argparse
import threading

from utils import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal

SERVER_HOST = 'localhost'
REQUEST_CREATE_ROOM = 'requestCreateRoom'
MESSAGE = 'message'
CLIENT_LIST = 'clientList'
GROUP_LIST = 'groupList'
GROUP_MESSAGE = 'groupMessage'
REQUEST_JOIN_ROOM = 'requestJoinRoom'

class ChatClient(QObject):
    workerSignal = pyqtSignal()
    createRoomSignal = pyqtSignal(str)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChatClient, cls).__new__(cls)
        return cls.instance

    """ A command line chat client using select """
    def initialisation(self, name = "client1", port=10000, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        self.connectedClientMap = {}
        self.chatHistory = {}
        self.roomHistory = {}
        self.roomMembers = {}
        
        # Initial prompt
        self.prompt = f'[{name}@{socket.gethostname()}]> '
        
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print(f'Now connected to chat server@ port {self.port}')
            self.connected = True
            
            # Send my name...
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)
            
            # Contains client address, set it
            addr = data.split('CLIENT: ')[1]
            self.assignedPort = int(addr)
            self.run()
        except socket.error as e:
            raise ValueError()
            print(f'Failed to connect to chat server @ port {self.port}')

    def cleanup(self):
        """Close the connection and wait for the thread to terminate."""
        self.sock.close()
    
    def background(self):
        while True:
            try:
                data = sys.stdin.readline().strip()
                if data =="quit":
                    self.cleanup()
                else:
                    send(self.sock, data)
            except KeyboardInterrupt:
                print(" Client interrupted. """)
                self.cleanup()

    def sendMessage(self, ipAddress, message):
        try:
            clientBAssignedPort = ipAddress[1]
            # Store message locally
            value = ["me",message]
            if clientBAssignedPort in self.chatHistory.keys():
                conversations = self.chatHistory[clientBAssignedPort]
                conversations.append(value)
                self.chatHistory[clientBAssignedPort]=conversations
            else:
                self.chatHistory[clientBAssignedPort]=[value]
            
            # Formating a message to send to server
            messageDict={}
            messageDict[self.assignedPort] = [self.name,message]
            sendMessage(self.sock, (ipAddress,messageDict))
        except socket.error as e:
            pass
    
    def sendGroupMessage(self, roomName, message):
        try:
            # Store message locally
            value = ["me",message]
            conversations = self.roomHistory[roomName]
            conversations.append(value)
            
            # Formating a message to send to server
            messageDict={}
            messageDict[roomName] = [self.name,message]
            print("The groupt message sent is:")
            print(messageDict)
            sendGroupMessage(self.sock, messageDict)
        except socket.error as e:
            pass


    def getConnectedClientAddress(self, name):
        for key in self.connectedClientMap.keys():
            if self.connectedClientMap[key] == name:
                return key
    
    def getConnectedClientAssignedPort(self,name):
        for key in self.connectedClientMap.keys():
            if self.connectedClientMap[key] == name:
                return key[1]

    def run(self):
        # Set up a background thread for user input
        threading1 = threading.Thread(target=self.background)
        threading1.daemon = True
        threading1.start()
        # send(self.sock, self.name)

        """ Chat client main loop """
        while self.connected:            
            # Wait for input from stdin and socket
            # readable, writeable, exceptional = select.select([self.sock], [], [])
            
            data = receive(self.sock)
            if not data:
                print('Client shutting down.')
                self.connected = False
                break
            else:
                messageType = list(data.keys())[0]
                if messageType == CLIENT_LIST:
                    self.connectedClientMap = data[CLIENT_LIST]
                    self.workerSignal.emit()
                elif messageType == MESSAGE:
                    self.receivePrivateMessage(data)
                elif messageType == REQUEST_CREATE_ROOM:
                    roomName = data[REQUEST_CREATE_ROOM]
                    self.roomHistory[roomName] = []
                    self.roomMembers[roomName] = []
                    print("The client has updated the following group message")
                    print(self.roomHistory)
                    self.createRoomSignal.emit(roomName)
                elif messageType == GROUP_MESSAGE:
                    frame = data[GROUP_MESSAGE]
                    roomName = list(frame.keys())[0]
                    message = frame[roomName]
                    self.roomHistory[roomName].append(message)
                    print("The client has updated the following group message")
                    print(self.roomHistory)
                elif messageType == GROUP_LIST:
                    frame = data[GROUP_LIST]
                    if frame != None:
                        for room in frame:
                            self.roomHistory[room] = []
                elif messageType == REQUEST_JOIN_ROOM:
                    frame = data[REQUEST_JOIN_ROOM]
                    roomName = list(frame.keys())[0]
                    members = frame[roomName]
                    self.roomMembers[roomName] = members

    def receivePrivateMessage(self, data):
        messageData = list(data.values())[0]
        for key in messageData.keys():
            if key in self.chatHistory.keys():
                chatMessages = self.chatHistory[key]
                chatMessages.append(messageData[key])
            else:
                self.chatHistory[key]=[messageData[key]]
    
    def createRoomRequest(self):
        sendCreateRoomRequest(self.sock, self.name)
            
    def joinRoomRequest(self, roomName):
        dataToSend = {}
        dataToSend[roomName] = self.name
        sendJoinRoomRequest(self.sock, dataToSend)


                


if __name__ == "__main__":
    client = ChatClient()
    client.initialisation()

#python3 chat_client.py --name ser --port 10000
