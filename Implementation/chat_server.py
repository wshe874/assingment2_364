import select
import socket
import sys
import signal
import argparse
import threading
import chat_client
import ssl
from group_database_server import GroupChatServer, Room


from utils import *

SERVER_HOST = 'localhost'


class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # list output sockets

        # Encryption
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
        self.context.load_verify_locations('cert.pem')
        self.context.set_ciphers('AES128-SHA')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)
        self.server = self.context.wrap_socket(self.server, server_side=True)

        self.groupDatabase = GroupChatServer()

        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port} ...')

    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))
    
    def background(self):
        while True:
            cmd = sys.stdin.readline().strip()
            if cmd == 'list':
                for output in self.outputs:
                    sendClientList(output, self.clientmap.values())
            elif cmd == 'quit':
                self.server.close()


    # Server start to listen to incoming messages from clients
    def run(self):
        inputs = [self.server]
        self.outputs = []

        # Set up a background thread for user input
        threading1 = threading.Thread(target=self.background)
        threading1.daemon = True
        threading1.start()

        # processing socket messages
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, [])
            except select.error as e:
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print(
                        f'Chat server: got connection {client.fileno()} from {address}')
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]

                    # Compute client name and send back
                    self.clients += 1

                    send(client, f'CLIENT: {str(address[1])}')
                    sendClientList(client,self.clientmap)

                    # Send all the current rooms
                    roomNames = self.groupDatabase.getAllRoomNames()
                    sendGroupList(client, roomNames)
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)

                    # Send joining information to other clients
                    for output in self.outputs:
                        newClientMap = self.clientmap.copy()
                        newClientMap.pop(output)
                        sendClientList(output, newClientMap)
                    self.outputs.append(client)                    
                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            messageType = list(data.keys())[0]
                            if messageType == MESSAGE:
                                self.processMessage(data)

                            if messageType == REQUEST_CREATE_ROOM:
                                self.processCreateRoomRequest(data)
                            
                            if messageType == GROUP_MESSAGE:
                                self.processGroupMessage(sock, data)
                            
                            if messageType == REQUEST_JOIN_ROOM:
                                self.procecessJoinRoomRequest(data)

                            if messageType == INVITATION:
                                self.processInvitation(sock, data)

                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            # Sending client leaving information to others
                            msg = f'\n(Now hung up: Client from {self.get_client_name(sock)})'

                            for output in self.outputs:
                                sendMessage(output, msg)
                    except socket.error as e:
                        print("no socket is found")
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        
        self.server.close()

    def processMessage(self, data):
        frame = data[MESSAGE]
        receiverAddress = frame[0]
        message = frame[1]
        for clientSocket in self.clientmap.keys():
            value = self.clientmap[clientSocket]
            if value[0] == receiverAddress:
                sendMessage(clientSocket, message)
                break

    def processCreateRoomRequest(self, data):
        creatorName = data[REQUEST_CREATE_ROOM]
        assignedPort = self.getClientAssignedPort(creatorName)
        creatorSock = self.getClientSocket(creatorName)
        roomName = self.groupDatabase.createRoom(creatorName, creatorSock, assignedPort)
        
        # Send the new room name to all connected members
        for clientSocket in self.outputs:
            sendCreateRoomRequest(clientSocket, roomName)

    def processGroupMessage(self, sock, data):
        frame = data[GROUP_MESSAGE]
        roomName = list(frame.keys())[0]
        memberSockets = self.groupDatabase.getAllRoomMemberSockets(roomName)
        for memberSocket in memberSockets:
            if sock == memberSocket:
                pass
            else:
                sendGroupMessage(memberSocket, frame)

    def procecessJoinRoomRequest(self, data):
        frame = data[REQUEST_JOIN_ROOM]
        roomName = list(frame.keys())[0]
        clientName = frame[roomName]

        if self.groupDatabase.checkIsMember(roomName, clientName):
            pass
        else:
            for key in self.clientmap.keys():
                value = self.clientmap[key]
                if clientName == value[1]:
                    assignedPort = value[0][1]
                    self.groupDatabase.joinRoom(roomName, clientName, key, assignedPort)
                    break
        memberSockets = self.groupDatabase.getAllRoomMemberSockets(roomName)
        members = self.groupDatabase.getAllRoomMembers(roomName)
        dataToSend={}
        dataToSend[roomName] = members
        for memberSocket in memberSockets:
            sendJoinRoomRequest(memberSocket, dataToSend)
    
    def processInvitation(self, sock, data):
        frame = data[INVITATION]
        roomName = list(frame.keys())[0]
        inviterName = self.getClientName(sock)
        invitedClients = frame[roomName]
        for sock in self.clientmap.keys():
            for client in invitedClients:
                if client == self.clientmap[sock][1]:
                    message = [inviterName,roomName]
                    sendInvitation(sock, message)

    def getClientAssignedPort(self, clientName):
        for key in self.clientmap.keys():
                value = self.clientmap[key]
                if clientName == value[1]:
                    assignedPort = value[0][1]
                    return assignedPort
    
    def getClientSocket(self, clientName):
        for key in self.clientmap.keys():
                value = self.clientmap[key]
                if clientName == value[1]:
                    return key
    
    def getClientName(self, socket):
        for sock in self.clientmap.keys():
            if socket == sock:
                return self.clientmap[sock][1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Socket Server Example with Select')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name

    server = ChatServer(port)
    server.run()
