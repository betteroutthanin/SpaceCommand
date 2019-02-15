import GameObjects.Modules

class Weapon(GameObjects.Modules.Module.Module):	

	def __init__(self):
		super(Weapon, self).__init__()

		self.LoggingPrefix = "Weapon"
		
		self.TargetGOBID = -1
		self.RangeLM = 0.1
		
	def SetTarget(self, GOBID):
		self.TargetGOBID = GOBID

	def TestFire(self):
		# TargetGOBID of -1 would imply that not target selected
		if (self.TargetGOBID == -1):
			return False

		# If the GOBID is valid, then ensure that the GOBID can be resolved to a
		# valid object
		GOB = self.MyUniverse.GOBID(GOBID)
		if (GOB is False):
			TargetGOBID = -1
			return False

		# We are good to fire, make sure the object is in range
		# Our Location is taken by our parent.  The Parent Must be a ship.
		ParentGOB = self.GetParentGOB()
		if (ParentGOB == False):
			return False

		if (isinstance(ParentGOB, GameObjects.Ships.Ship.Ship) == False):			
			return False

		pass




		
	
	
