import GameObjects.Modules.Computers.Computer

class Server(GameObjects.Modules.Computers.Computer.Computer):	

	def __init__(self):
		super(Server, self).__init__()

		self.LoggingPrefix = "Server"

		self.CommandRoutingTable['Kill'] = "ProcessKill"
		self.CommandRoutingTable['ListGOBs'] = "ProcessListGOBs"
		self.CommandRoutingTable['Help'] = "ProcessHelp"
		self.CommandRoutingTable['SaveAll'] = "ProcessSaveAll"

	def RouteCommandToModule(self, CommandString):
		# Server command routing is handled differently in the server vs the standard
		# computer

		# Convert the command string into a usable structure
		NewCommand = GameObjects.Modules.Computers.Computer.Command()
		result = NewCommand.GenerateCommandFromString(CommandString)
		if (result != True):
			return result

		# Run the command
		result = self.ProcessCommand(NewCommand)
		return result

	def ProcessKill(self, TheCommand):
		self.MyUniverse.RSC_KillServer()
		return "Server Shutting down"

	def ProcessListGOBs(self, TheCommand):
		return "Todo"

	def ProcessHelp(self, TheCommand):
		return str(self.CommandRoutingTable)

	def ProcessSaveAll(self, TheCommand):
		self.MyUniverse.RSC_SaveAllGOBs()
		return "All objects saved"
