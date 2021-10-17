import sys
import threading
import time
from chat_client import ChatClient
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QCheckBox, QListWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit

class Connect(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        vbox = QVBoxLayout()

        #input text fileds
        grid = QGridLayout()

        grid.addWidget(QLabel('IP Address:'), 0, 0)
        grid.addWidget(QLabel('Port:'), 1, 0)
        grid.addWidget(QLabel('Nick Name:'), 2, 0)

        self.ipAddress = QLineEdit()
        self.port = QLineEdit()
        self.nickName = QLineEdit()

        grid.addWidget(self.ipAddress, 0, 1)
        grid.addWidget(self.port, 1, 1)
        grid.addWidget(self.nickName, 2, 1)

        #buttons
        hbox = QHBoxLayout()
        connectButton = QPushButton('Connect', self)
        connectButton.setCheckable(True)
        connectButton.toggle()
        connectButton.clicked.connect(self.connect)

        cancelButton = QPushButton('Cancel',self)
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(connectButton)
        hbox.addWidget(cancelButton)

        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setWindowTitle('Chat Room')
        self.resize(500,500)

    def connect(self):
        self.ip = self.ipAddress.text()
        self.port = self.port.text()
        self.name = self.nickName.text()

        try:
            self.client = ChatClient()
            # Set up a background thread for user input
            self.threading1 = threading.Thread(target=self.background)
            self.threading1.start()
            self.client.workerSignal.connect(self.finished)
            
        except ValueError as e:
            pass
    
    def finished(self):
        self.switch_window.emit()
    
    # Running on background to receive messages from server
    def background(self):
        self.client.initialisation(name=self.name, port=int(self.port), host=self.ip)                
class Connected(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(int, str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.pageOpen = True
        vbox = QVBoxLayout()
        font = self.font()
        font.setPointSize(14)

        # Display a list of connect clients
        privateChatLabel = QLabel("Connected Clients")
        privateChatLabel.setFont(font)
        noticeMessage = QLabel("*Click on a person to chat")
        self.listClients = QListWidget()
        self.listClients.clicked.connect(self.privateChat)


        # Display a list of groups
        groupChatLabel = QLabel("Chats rooms (Group chat)")
        groupChatLabel.setFont(font)
        noticeMessage2 = QLabel("*Click on a group to join a group chat")
        self.listGroups = QListWidget()
        self.listGroups.clicked.connect(self.groupChat)

        
        # Create new group chats
        connectButton = QPushButton('CREATE A GROUP CHAT', self)
        connectButton.clicked.connect(self.createGroup)

        
        # Back to connection page
        cancelButton = QPushButton('Back',self)
        cancelButton.clicked.connect(self.back)

        vbox.addWidget(privateChatLabel)
        vbox.addWidget(noticeMessage)
        vbox.addWidget(self.listClients)
        vbox.addWidget(groupChatLabel)
        vbox.addWidget(noticeMessage2)
        vbox.addWidget(self.listGroups)
        vbox.addWidget(connectButton)
        vbox.addWidget(cancelButton)
        self.setLayout(vbox)

        self.setWindowTitle('Chat Room')
        self.resize(500,500)
        self.generatePageLists()
        # Set up a background thread for receiving message
        threading1 = threading.Thread(target= self.background)
        threading1.start()
    
    def back(self):
        self.pageOpen = False
        self.switch_window.emit(3, "back")

    def privateChat(self):
        self.pageOpen = False
        name = self.listClients.selectedItems()[0].text()
        self.switch_window.emit(0,name)

    def groupChat(self):
        self.pageOpen = False
        client = ChatClient()
        roomName = self.listGroups.selectedItems()[0].text()
        client.joinRoomRequest(roomName)
        self.switch_window.emit(1, roomName)

    def createGroup(self):
        client = ChatClient()
        client.createRoomRequest()
        client.createRoomSignal.connect(self.jumpToRoom)
    
    def jumpToRoom(self, roomName):
        self.pageOpen = False
        client = ChatClient()
        client.roomMembers[roomName] = [client.name]
        self.switch_window.emit(2, roomName)
    
    def generatePageLists(self):
        # Clean the lists
        self.listClients.clear()
        self.listGroups.clear()
        connectedClient = ChatClient()

        # Populate the clients
        clients = connectedClient.connectedClientMap.keys()
        for client in clients:
            self.listClients.addItem(connectedClient.connectedClientMap[client])

        # Populate the rooms
        rooms = connectedClient.roomHistory.keys()
        for room in rooms:
            self.listGroups.addItem(room)
    
    def background(self):
        while self.pageOpen is True:
            self.generatePageLists()
            time.sleep(5)
    def setPageOpenTrue(self):
        self.pageOpen = True

class PrivateChat(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self, name):
        QtWidgets.QWidget.__init__(self)
        self.pageOpen = True
        self.client = ChatClient()
        self.clientName = name
        self.roomName = "Chat with "+name
        self.initUI()
        # Set up a background thread for receiving message
        threading1 = threading.Thread(target= self.background)
        threading1.start()
        

    def initUI(self):
        vbox = QVBoxLayout()
        font = self.font()
        font.setPointSize(14)

        # Chat history
        client = ChatClient()
        client.connectedClientMap
        labelText = self.roomName
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        self.chatList = QListWidget()

        # Sending messages
        hbox = QHBoxLayout()
        sendButton = QPushButton('Send', self)
        sendButton.clicked.connect(self.sendMessage)
        self.inputText = QtWidgets.QLineEdit()
        hbox.addWidget(self.inputText)
        hbox.addWidget(sendButton)

        # Go back to connected page
        cancelButton = QPushButton('Back',self)
        cancelButton.clicked.connect(self.back)

        vbox.addWidget(titleLabel)
        vbox.addWidget(self.chatList)
        vbox.addLayout(hbox)
        vbox.addWidget(cancelButton)

        self.generateMessagesList(self.clientName)
        self.setLayout(vbox)
        self.resize(500,500)

    def background(self):
        while self.pageOpen is True:
            self.generateMessagesList(self.clientName)
            time.sleep(5)

    def sendMessage(self):
        client = ChatClient()
        clientAddress = client.getConnectedClientAddress(self.clientName)
        client.sendMessage(ipAddress=clientAddress, message=self.inputText.text())
        self.inputText.setText('')
        self.generateMessagesList(self.clientName)
    
    def generateMessagesList(self, name):
        client = ChatClient()
        assignedPort = client.getConnectedClientAssignedPort(name)
        self.chatList.clear()

        if assignedPort in client.chatHistory.keys():
            for message in client.chatHistory[assignedPort]:
                self.chatList.addItem(message[0]+': '+message[1])

    def back(self):
        self.pageOpen=False
        self.switch_window.emit()
class GroupChat(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(int)

    def __init__(self, roomName):
        QtWidgets.QWidget.__init__(self)
        self.pageOpen = True
        self.roomName = roomName
        self.initUI()
        # Set up a background thread for receiving message
        threading1 = threading.Thread(target= self.background)
        threading1.start()


    def initUI(self):
        horizontalLayout = QHBoxLayout()
        font = self.font()
        font.setPointSize(14)

        # Chating side of screen
        chatSide = QVBoxLayout()

        # Chat history
        labelText = self.roomName
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        self.roomChats = QListWidget()

        # Sending messages
        hbox = QHBoxLayout()
        sendButton = QPushButton('Send', self)
        sendButton.clicked.connect(self.sendMessage)
        self.inputText = QtWidgets.QLineEdit()
        hbox.addWidget(self.inputText)
        hbox.addWidget(sendButton)

        # Go back to connected page
        cancelButton = QPushButton('Back',self)
        cancelButton.clicked.connect(self.back)

        chatSide.addWidget(titleLabel)
        chatSide.addWidget(self.roomChats)
        chatSide.addLayout(hbox)
        chatSide.addWidget(cancelButton)
        
        # Showing joined members
        memberSide = QVBoxLayout()
        labelText = "Member"
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        self.listMembers = QListWidget()

        inviteButton = QPushButton('Invite',self)
        inviteButton.clicked.connect(self.invite)
        memberSide.addWidget(titleLabel)
        memberSide.addWidget(self.listMembers)
        memberSide.addWidget(inviteButton)

        horizontalLayout.addLayout(chatSide, 7)
        horizontalLayout.addLayout(memberSide, 3)
        self.generateMessagesList(self.roomName)

        self.setLayout(horizontalLayout)

        self.resize(500,500)
    
    def generateMessagesList(self, roomName):
        self.roomChats.clear()
        client = ChatClient()
        print(client.roomHistory)
        for message in client.roomHistory[roomName]:
            self.roomChats.addItem(message[0]+': '+message[1])
    
    def generateMemberList(self, roomName):
        self.listMembers.clear()
        client = ChatClient()
        print(client.roomMembers)
        if roomName in client.roomMembers.keys():
            for member in client.roomMembers[roomName]:
                self.listMembers.addItem(member)
    
    def sendMessage(self):
        print("Sending a message")
        print(self.inputText.text())
        client = ChatClient()
        client.sendGroupMessage(self.roomName, self.inputText.text())
        self.inputText.setText('')
        self.generateMessagesList(self.roomName)
    
    def back(self):
        self.pageOpen = False
        self.switch_window.emit(0)   

    def invite(self):
        print("invite")
        self.switch_window.emit(1)
    
    def background(self):
        while self.pageOpen is True:
            self.generateMessagesList(self.roomName)
            self.generateMemberList(self.roomName)
            print("background is running")
            time.sleep(5)

class Invite(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.invitingList = []
        self.initUI()

    def initUI(self):
        verticalLayout = QVBoxLayout()
        font = self.font()
        font.setPointSize(14)
        
        # Showing connected clients
        labelText = "Connected Clients"
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        self.listClients = QVBoxLayout()

        self.listClients = QListWidget()
        self.listClients.addItem("Alice")
        self.listClients.addItem("Bob")
        self.listClients.addItem("Alice")
        self.listClients.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listClients.clicked.connect(self.addToInvitingList)

        hbox = QHBoxLayout()
        inviteButton = QPushButton('Invite',self)
        inviteButton.clicked.connect(self.invite)

        cancelButton = QPushButton('Cancel',self)
        cancelButton.clicked.connect(self.back)
        hbox.addWidget(inviteButton)
        hbox.addWidget(cancelButton)

        verticalLayout.addWidget(titleLabel)
        verticalLayout.addWidget(self.listClients)
        verticalLayout.addLayout(hbox)

        self.setLayout(verticalLayout)

        self.resize(500,500)
    
    
    def back(self):
        print("go back")
        self.switch_window.emit()   

    def invite(self):
        print("invite")
        #Invite the clients
        self.confirmDialog()
        self.switch_window.emit()
    
    def confirmDialog(self):
        dlg = QMessageBox(self)
        dlg.setText("Invitation has been sent.")
        button = dlg.exec()

        if button == QMessageBox.Ok:
            print("OK!")
    
    def addToInvitingList(self):
        items = self.listClients.selectedItems()
        self.invitingList = []
        for i in range(len(items)):
            self.invitingList.append(str(self.listClients.selectedItems()[i].text()))
        print (self.invitingList)


class Controller:

    def __init__(self):
        pass

    def showConnect(self):
        self.connect = Connect()
        self.connect.switch_window.connect(self.showConnected)
        self.connect.show()
    
    def showConnected(self):
        self.connected = Connected()
        self.connected.switch_window.connect(self.connectedPageOptions)
        self.connect.close()
        self.connected.show()
    
    def showPrivateRoom(self, name):
        self.client = PrivateChat(name)
        self.client.switch_window.connect(self.backFromPrivateRoom)
        self.connected.close()
        self.client.show()
    
    def backFromPrivateRoom(self):
        self.connected = Connected()
        self.connected.switch_window.connect(self.connectedPageOptions)
        self.client.close()
        self.connected.show()
    
    def showGroupChat(self, roomName):
        self.group = GroupChat(roomName)
        self.group.switch_window.connect(self.groupChatPageOptions)
        self.connected.close()
        self.group.show()
    
    def showInvitation(self):
        self.invitation = Invite()
        self.invitation.switch_window.connect(self.invitationOption)
        self.invitation.show()

    
    def connectedPageOptions(self, option, argument=""):
            if option == 0:
                self.showPrivateRoom(argument)
            elif option == 1:
                self.showGroupChat(argument)
            elif option == 2:
                self.showGroupChat(argument)
            else:
                self.showConnect()
    
    def groupChatPageOptions(self, option):
        if option == 0:
            self.group.close()
            self.connected.setPageOpenTrue()
            self.connected.show()
        else:
            self.showInvitation()
            print("show inivation screen")
    
    def invitationOption(self):
        self.invitation.close()
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.showConnect()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#python3 chat_server.py --name server --port 10000