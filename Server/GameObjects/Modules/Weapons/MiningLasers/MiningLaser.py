import GameObjects.Modules.Weapons.Weapon

class MiningLaser(GameObjects.Modules.Weapons.Weapon.Weapon):	

	def __init__(self):
		super(MiningLaser, self).__init__()

		self.LoggingPrefix = "MiningLaser"

	def Tick(self):
		pass
