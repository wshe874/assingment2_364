
class GroupChatServer():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GroupChatServer, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.rooms = []
        self.globalId = 1
    
    def createRoom(self, creatorName,socket, assignedPort):
        roomName = 'Room '+ str(self.globalId) + " by " + creatorName
        newRoom = Room(self.globalId,roomName, creatorName)
        newRoom.addOtherInfo(socket, assignedPort, creatorName)
        self.rooms.append(newRoom)
        
        self.globalId = self.globalId+1
        return roomName
    
    def getAllRoomMemberSockets(self, roomName):
        for room in self.rooms:
            if room.name == roomName:
                return room.sockets
    
    def getAllRoomNames(self):
        roomNames = []
        for room in self.rooms:
            roomNames.append(room.name)
        return roomNames
    
    def checkIsMember(self, roomName, clientName):
        for room in self.rooms:
            if room.name == roomName:
                if clientName in room.joinedMembers:
                    return True
        return False
    
    def joinRoom(self, roomName, clientName, socket, assignedPort):
        for room in self.rooms:
            if room.name == roomName:
                room.addMember(clientName, socket, assignedPort)
    
    def getAllRoomMembers(self, roomName):
        for room in self.rooms:
            if room.name == roomName:
                return room.joinedMembers


class Room():
    def __init__(self, id, name, creatPersonName):
        self.id = id
        self.name = name
        self.creatPersonName = creatPersonName
        self.joinedMembers = []
        self.sockets = []
        self.assignedPorts = []
    
    def addMember(self, memberName, socket, assignedPort):
        self.joinedMembers.append(memberName)
        self.sockets.append(socket)
        self.assignedPorts.append(assignedPort)
    
    def getSockets(self):
        return self.sockets
    
    def addOtherInfo(self, socket, assignedPort, memberName):
        self.sockets.append(socket)
        self.joinedMembers.append(memberName)
        self.assignedPorts.append(assignedPort)

