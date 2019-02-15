import time
import telnetlib
import Queue

class StateMachine(object):
	State = False
	Option = False
	Connection = False
	InputBuffer = False
	Partial = False
	EventRouter = False

	def __init__(self):

		self.InputBuffer = []
		self.Partial = ""

		self.Options = {}
		self.Options["State_StartLogin"] = self.State_StartLogin
		self.Options["State_WaitLogin"] = self.State_WaitLogin
		self.Options["State_DoStuff"] = self.State_DoStuff

		self.EventRouter = {}
		self.AddEventHandler("LoginRequest", self.Handle_LoginRequest)
		self.AddEventHandler("LoggedIn", self.Handle_LoggedIn)

		# First State
		self.State = "State_StartLogin"

	def StateLoop(self):
		while 1:
			State = self.State
			# print("==> State = " + State)

			self.UpdateInputBuffer()
			self.ProcessInputBuffer()

			self.Options[State]()
			time.sleep(1)

	# Event and Messaging system
	def AddEventHandler(self, EventName, Handler):
		self.EventRouter[EventName] = Handler

	def RemoveEvent(self, EventName):
		self.EventRouter[EventName] = False

	def ProcessEvent(self, Event):
		print str(Event)
		if (Event['Name'] in self.EventRouter):
			self.EventRouter[Event['Name']](Event)

	def ProcessInputBuffer(self):
		for Value in self.InputBuffer:
			Line = self.InputBuffer.pop()
			print "Event = " + str(Line)
			# Event:Drive:Destination Reached:" + str(self.Destination)

			LineParts = Line.split(":")
			Event = False
			if (len(LineParts) == 4):
				if (LineParts[0].strip() == "Event"):
					print "Building an event"
					# Got an Event
					Event = {}
					Event['Source'] = LineParts[1].strip()
					Event['Name'] = LineParts[2].strip()
					Event['Data'] = LineParts[3].strip()

				if (Event != False):
					self.ProcessEvent(Event)
			else:
				print "Message was not an event"
				print "   " + str(LineParts)
				# todo - deal with this

	def SendMessage(self, Message):
		self.Connection.write(str(Message) + "\n")

	def UpdateInputBuffer(self):
		if (self.Connection != False):
			Input = self.Connection.read_until("\n", 0)

			SplitInput = Input.split("\n")

			# Holy Shit, we will assume that no partial strings will be sent
			# if the last entry is a "" then the last charater was a \n
			SplitSize = len(SplitInput)
			if (SplitInput[SplitSize - 1] != ''):
				print "Got a partial !!!!!!!!!"

			for Line in SplitInput:
				if (len(Line) > 0):
					# Line must be stripped for clean up
					self.InputBuffer.append(Line.strip())

	def State_StartLogin(self):
		self.Connection = telnetlib.Telnet("localhost", 7777)
		self.State = "State_WaitLogin"

	def State_WaitLogin(self):
		pass

	def Handle_LoginRequest(self, EventData):
		self.SendMessage("2:pass")

	def Handle_LoggedIn(self, EventData):
		self.State = "State_DoStuff"