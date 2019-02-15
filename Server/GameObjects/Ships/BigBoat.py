import GameObjects.Ships.Ship

class BigBoat(GameObjects.Ships.Ship.Ship):
	
	def __init__(self):
		super(BigBoat, self).__init__()

		self.LoggingPrefix = "Ship/BigBoat"

		# Children should of been defined in the GameObject Init
		self.Children[0] = self.CreateModuleSlot("GameObjects.Modules.Drives.Drive.Drive", 1)
		self.Children[1] = self.CreateModuleSlot("GameObjects.Modules.Computers.Computer.Computer", 1)
		self.Children[2] = self.CreateModuleSlot("GameObjects.Modules.Module.Module", 1)
		self.Children[3] = self.CreateModuleSlot("GameObjects.Modules.Module.Module", 1)		