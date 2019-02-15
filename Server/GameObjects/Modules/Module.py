import GameObject

class Module(GameObject.GameObject):
	
	def __init__(self):
		super(Module, self).__init__()

		self.LoggingPrefix = "Module"

		# Class
		self.Class = 1

		self.GetAbleList = []
		self.SetAbleList = []
		self.CommandRoutingTable = {}

		self.GetAbleList = ['ID']

		# Core commands for all modules
		self.CommandRoutingTable['Set']    = "ProcessSet"
		self.CommandRoutingTable['Get']    = "ProcessGet"
		self.CommandRoutingTable['GetPos'] = "ProcessGetPos"
		self.CommandRoutingTable['Info']   = "ProcessInfo"        

		self.GetAbleList.append("LoggingPrefix");

	# ----------------------------------------
	# Module Command Processing

	def ProcessCommand(self, TheCommand):
		# Look for the "Call" in the CommandRoutingTable, if the Call doesn't exist
		# then the module will be unable to process the command
		
		self.LogMe("ProcessCommand = " + str(TheCommand.Call))
		
		if (TheCommand.Call in self.CommandRoutingTable.keys()):
			CommandName = self.CommandRoutingTable[TheCommand.Call]

			try:
				Method = getattr(self, CommandName)
			except:
				return "Command failed: Command is in routing table, but module doesn't support method"

			# And Run the command
			result = Method(TheCommand)
			return result
		else:
			return "Command failed: Module has no router register for command ->" + TheCommand.Call

	def ProcessSet(self, TheCommand):

		VarName = TheCommand.Parm[0]
		NewValue = TheCommand.Parm[1]

		# Make sure the Variable that is about to be set is in the SetAble List
		# otherwise Code.py may steam roll variables we don't want them to have
		# access to
		if (VarName in self.SetAbleList):

			# Ensure that the variable is part of the module
			try:
				OriginalValue = getattr(self, VarName)
			except:
				return "Command failed: Value is not part of this module -> " + VarName

			# Force a conversion of types so the passed value matches the original
			# value type.  Note that the ConversionWithTypeMatch returns a dict as
			# a result
			Result = self.ConversionWithTypeMatch(OriginalValue, NewValue)
			ConvertedValue = Result['Value']
			Outcome = Result['Outcome']

			if (Outcome is False):
				return "Command failed: Failed to convert new variable to target type"
			else:
				setattr(self, VarName, ConvertedValue)
				return "True"
		else:
			return "Command failed: Variable is not SetAble -> " + VarName

	def ProcessGet(self, TheCommand):
		# Make sure the Variable that is about to be get is in the GetAble List
		# otherwise Code.py may read things it is not suppose to
		VarName = TheCommand.Parm[0]

		if (VarName in self.GetAbleList):
			return getattr(self, VarName)
		else:
			return "Command failed: Variable is not GetAble -> " + VarName

	def ProcessGetPos(self, TheCommand):
		# Special case so that the position can be passed back in a unified format
		return self.PositionToString(self.GetPos())

	def ProcessInfo(self, TheCommand):
		return str(self.__class__.__name__)

class ModuleEvent():
	def __init__(self, ModuleName, EventName, EventData):
		self.ModuleName = ModuleName
		self.EventName = EventName
		self.EventData = EventData
