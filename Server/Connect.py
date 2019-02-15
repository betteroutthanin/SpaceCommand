import miniboa
import datetime

import Base

class ConnectionManager(Base.Base):
	
	def __init__(self):
		super(ConnectionManager, self).__init__()

		self.LoggingEnabled = False
		self.LoggingPrefix = "ConnectionManager"

		self.TheUniverse = False

		self.ConnectionList = []
		self.TelnetServer = miniboa.TelnetServer(port=7777, address='', on_connect=self.on_connect, on_disconnect=self.on_disconnect, timeout = .05)

	def Boot(self):
		pass

	def on_connect(self, Connection):
		Connection.send("Welcome to the Space Command Router\n")
		Connection.ConnectedToCompter = False
		Connection.ComputerObjectID = -1
		Connection.CommandBuffer = []
		Connection.NonBoundState = "Start"
		self.ConnectionList.append(Connection)

	def on_disconnect(self, Connection):
		self.LogMe("Connection lost -> " + str(Connection.addrport()))
		self.ConnectionList.remove(Connection)

	def ProcessConnections(self):
		# self.LogMe("ProcessConnections")

		for Connection in self.ConnectionList:
			self.ProcessConnection(Connection)

	def ProcessConnection(self, Connection):
		self.LogMe("ProcessConnection for " + str(Connection.addrport()))

		# Connection may not yet be bound to a computer
		if (Connection.ComputerObjectID == -1):
			self.ProcessNonBoundConnection(Connection)
		else:
			# We are bound to the object
			self.ProcessBoundConnection(Connection)

	def ProcessBoundConnection(self, Connection):
		# Resolve the the comptuer object each pass, just incase it has been killed
		ComputerObject = self.TheUniverse.GOBID(Connection.ComputerObjectID)
		if (ComputerObject is False):
			Connection.send("Connection to computer object lost'\n")
			Connection.ComputerObjectID = -1
			Connection.NonBoundState = "Start"
			return

		# Output buffer of the computer may need to be sent
		Queue = ComputerObject.EventBuffer
		while (Queue.empty() == False):
			Message = str(Queue.get() + "\n")
			Connection.send(Message)

		# Route inputs back to the computer
		msg = Connection.get_command()
		if (msg == None):
			return

		# Tell the computer to run the command
		# assumes that RunCommand will return a string
		ResultOfRun = ComputerObject.CI.RunCommand(msg) + "\n"
		Connection.send(ResultOfRun)

	def ProcessNonBoundConnection(self, Connection):
		Options = {}
		Options["Start"] = self.PresentLoginRequest
		Options["WaitingForLoginDetails"] = self.ProcessLogin

		State = Connection.NonBoundState
		self.LogMe("NonBoundState = " + State)
		Options[State](Connection)

	def PresentLoginRequest(self, Connection):
		Connection.send("Event:Connector:LoginRequest:None\n")
		Connection.NonBoundState = "WaitingForLoginDetails"

	def ProcessLogin(self, Connection):
		self.LogMe("ProcessLogin - Checing for Data")
		msg = Connection.get_command()
		if (msg == None):
			return

		self.LogMe("ProcessLogin - Got Data")

		# we have a login attempt
		Parts =  msg.split(":", 1)
		if (len(Parts) != 2):
			Connection.send("Event:Connector:Error:Last Login Failed - not enough parts\n")
			Connection.NonBoundState = "Start"
			return

		self.LogMe("ProcessLogin - Split done")

		# First part must be an int (is what GOBID will want)
		try:
			ComputerObjectID = int(Parts[0])
			Password = Parts[1]
		except:
			Connection.send("Event:Connector:Error:Last Login Failed - ID not an Int\n")
			Connection.NonBoundState = "Start"
			return

		self.LogMe("ProcessLogin - Split bound")

		# Try to get the object
		ComputerObject = self.TheUniverse.GOBID(ComputerObjectID)
		if (ComputerObject is False):
			Connection.send("Event:Connector:Error:Last Login Failed - GOBID not Found\n")
			Connection.NonBoundState = "Start"
			return

		self.LogMe("ProcessLogin - Got Computer Object")

		# Check the Password
		if (ComputerObject.CheckPassWord(Password) == False):
			Connection.send("Event:Connector:Error:Last Login Failed - Password\n")
			Connection.NonBoundState = "Start"
			return

		self.LogMe("ProcessLogin - Password is good")

		# Ding
		Connection.ComputerObjectID = ComputerObjectID
		Connection.send("Event:Connector:LoggedIn:None\n")

		self.LogMe("ProcessLogin - Login complete")

	def poll(self):
		self.TelnetServer.poll()
