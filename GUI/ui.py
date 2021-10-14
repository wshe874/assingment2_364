import sys
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

        grid.addWidget(QLineEdit(), 0, 1)
        grid.addWidget(QLineEdit(), 1, 1)
        grid.addWidget(QLineEdit(), 2, 1)

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
        self.switch_window.emit()

class Connected(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(int, str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        vbox = QVBoxLayout()
        font = self.font()
        font.setPointSize(14)

        # Display a list of connect clients
        privateChatLabel = QLabel("Connected Clients")
        privateChatLabel.setFont(font)
        noticeMessage = QLabel("*Click on a person to chat")
        listClients = QListWidget()
        listClients.addItem("private chat")
        listClients.clicked.connect(self.privateChat)

        # Display a list of groups
        groupChatLabel = QLabel("Chats rooms (Group chat)")
        groupChatLabel.setFont(font)
        noticeMessage2 = QLabel("*Click on a group to join a group chat")
        listGroups = QListWidget()
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.addItem("public chat")
        listGroups.clicked.connect(self.groupChat)

        # Create new group chats
        connectButton = QPushButton('CREATE A GROUP CHAT', self)
        connectButton.clicked.connect(self.createGroup)
        
        # Back to connection page
        cancelButton = QPushButton('Back',self)
        cancelButton.clicked.connect(self.back)

        vbox.addWidget(privateChatLabel)
        vbox.addWidget(noticeMessage)
        vbox.addWidget(listClients)
        vbox.addWidget(groupChatLabel)
        vbox.addWidget(noticeMessage2)
        vbox.addWidget(listGroups)
        vbox.addWidget(connectButton)
        vbox.addWidget(cancelButton)
        self.setLayout(vbox)

        self.setWindowTitle('Chat Room')
        self.resize(500,500)

    def back(self):
        self.switch_window.emit(3, "back")

    def privateChat(self):
        self.switch_window.emit(0,"hello")

    
    def groupChat(self):
        self.switch_window.emit(1, "hi")

    
    def createGroup(self):
        self.switch_window.emit(2, "create")

class PrivateChat(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        font = self.font()
        font.setPointSize(14)

        # Chat history
        labelText = "Chat With Alice"
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        chatHistory = QListWidget()
        chatHistory.addItem("Alice (08:24): Hi")

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
        vbox.addWidget(chatHistory)
        vbox.addLayout(hbox)
        vbox.addWidget(cancelButton)
        self.setLayout(vbox)

        self.resize(500,500)
    
    def sendMessage(self):
        print("Sending a message")
        print(self.inputText.text())
    
    def back(self):
        self.switch_window.emit()

class GroupChat(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(int)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        horizontalLayout = QHBoxLayout()
        font = self.font()
        font.setPointSize(14)


        # Chating side of screen
        chatSide = QVBoxLayout()

        # Chat history
        labelText = "Room 1 by Alice"
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        chatHistory = QListWidget()
        chatHistory.addItem("Alice (08:24): Hi")

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
        chatSide.addWidget(chatHistory)
        chatSide.addLayout(hbox)
        chatSide.addWidget(cancelButton)
        
        # Showing joined members
        memberSide = QVBoxLayout()
        labelText = "Member"
        titleLabel = QLabel(labelText)
        titleLabel.setFont(font)
        listMembers = QListWidget()
        listMembers.addItem("Alice (Host)")

        inviteButton = QPushButton('Invite',self)
        inviteButton.clicked.connect(self.invite)
        memberSide.addWidget(titleLabel)
        memberSide.addWidget(listMembers)
        memberSide.addWidget(inviteButton)

        horizontalLayout.addLayout(chatSide, 7)
        horizontalLayout.addLayout(memberSide, 3)

        self.setLayout(horizontalLayout)

        self.resize(500,500)
    
    def sendMessage(self):
        print("Sending a message")
        print(self.inputText.text())
    
    def back(self):
        print("go back")
        self.switch_window.emit(0)   

    def invite(self):
        print("invite")
        self.switch_window.emit(1)

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
    
    def showPrivateRoom(self):
        self.client = PrivateChat()
        self.client.switch_window.connect(self.backFromPrivateRoom)
        self.connected.close()
        self.client.show()
    
    def backFromPrivateRoom(self):
        self.connected = Connected()
        self.connected.switch_window.connect(self.connectedPageOptions)
        self.client.close()
        self.connected.show()
    
    def showGroupChat(self):
        self.group = GroupChat()
        self.group.switch_window.connect(self.groupChatPageOptions)
        self.connected.close()
        self.group.show()
    
    def showInvitation(self):
        self.invitation = Invite()
        self.invitation.switch_window.connect(self.invitationOption)
        self.invitation.show()

    
    def connectedPageOptions(self, option, argument=""):
            if option == 0:
                self.showPrivateRoom()
            elif option == 1:
                self.showGroupChat()
            elif option == 2:
                print("clicked on create")
            else:
                self.showConnect()
    
    def groupChatPageOptions(self, option):
        if option == 0:
            self.group.close()
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