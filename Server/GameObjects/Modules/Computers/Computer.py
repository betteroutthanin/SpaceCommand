import Queue

import GameObjects.Modules.Module

class Computer(GameObjects.Modules.Module.Module):	

	def __init__(self):
		super(Computer, self).__init__()

		self.LoggingPrefix = "Computer"

		# Computers can be connected to externally by telnet sessions
		# a password in used to handle security
		self.Password = "pass"

		# OutBuffer _ connection will read this little sucker
		# The outbuffer will use the queue object
		self.EventBuffer = Queue.Queue()

		# Command Interface
		self.CI = CommandInterface()
		self.CI.SetComputer(self)

		self.CommandRoutingTable['ListModules'] = "ProcessListModules"

	def Tick(self):
		super(Computer, self).Tick()

	def AddEvent(self, EventString):
		self.EventBuffer.put(EventString)

	def SetConnection(self, Connection):
		self.Connection = Connection

	def CheckPassWord(self, PasswordToCheck):
		if (PasswordToCheck == self.Password):
			return True
		else:
			return False

	def ProcessListModules(self, TheCommand):

		Buffer = ""

		# Find the ship, it should be the parent object
		ParentGameObject = self.MyUniverse.GOBID(self.OwnerID)
		if (ParentGameObject is False):
			return "Command Failed: Failed to find computers OwnerID Game Object"

		return ParentGameObject.GenerateModuleListAsString()		

	def RouteCommandToModule(self, CommandString):

		# Convert the command string into a usable structure
		NewCommand = Command()
		result = NewCommand.GenerateCommandFromString(CommandString)
		if (result != True):
			return result

		# The computer has to pass this off to a module in the ship.
		if (self.OwnerID == -1):
			return "Command Failed: Computer doesn't have a parent, OwnerID = -1"

		# The parent object is needed so that we can do a slot look up in its
		# children
		ParentGameObject = self.MyUniverse.GOBID(self.OwnerID)
		if (ParentGameObject is False):
			return "Command Failed: Failed to find computers OwnerID Game Object"

		# Pass the command over to the module in the slot . . . if it exists
		TargetSlot = NewCommand.TargetModuelSlot
		TargetGameObjectID = ParentGameObject.Children[TargetSlot].GameObjectID

		# The module slot may be empty
		if (TargetGameObjectID == -1):
			return "Command Failed: Computers parent doesn't have a defined object in that slot"

		# The defined ID in that slot may not resolve to an actual object
		TargetGameObject = self.MyUniverse.GOBID(TargetGameObjectID)
		if (TargetGameObject is False):
			return "Command Failed: Computer failed to get the game object that was defined in the slot"

		result = TargetGameObject.ProcessCommand(NewCommand)
		return result

class CommandInterface():
	def __init__(self):	
		self.__TheComputer = False

	def SetComputer(self, Puta):
		self.__TheComputer = Puta

	def RunCommand(self, CommandString):
		return str(self.__TheComputer.RouteCommandToModule(CommandString))

class Command():
	def GenerateCommandFromString(self, CommandString):
		# Simple Command Example
		# 0:set cat 600
		# 0 = Slot ID
		# set = command
		# cat = parm 1
		# 600 = parm 2

		# Make sure there is enough data to support the : split
		# this will give us some core parts
		Parts =  CommandString.split(":")
		if (len(Parts) != 2):
			return "Command Failed: Initial Split didn't produce 2 parts (:)"

		# Slot ID
		IDStr = Parts[0]
		try:
			ID = int(IDStr)
		except:
			return "Command failed: Slot ID is not a number -> " + IDStr
		self.TargetModuelSlot = ID

		# Break Down the sub Parts
		# Make sure the spaces are trimmed of either end.  It seems to cause problems
		# if we have something like this '0: set' vs '0:set'
		Parts[1] = Parts[1].strip()
		SubParts = Parts[1].split(" ")
		self.Call = "blank"
		self.Parm = [False, False]

		try:
			self.Call = SubParts[0]
		except:
			pass

		try:
			self.Parm[0] = SubParts[1]
		except:
			pass

		try:
			self.Parm[1] = SubParts[2]
		except:
			pass

		# Dump
		# self.LogMe("  TargetModuelSlot -> " + str(self.TargetModuelSlot))
		# self.LogMe("  Call -> " + self.Call)
		# self.LogMe("  Parm 0 -> " + self.Parm[0])
		# self.LogMe("  Parm 1 -> " + self.Parm[1])

		return True
