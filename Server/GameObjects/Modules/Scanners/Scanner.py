import Base
import GameObjects.Modules.Module

class Scanner(GameObjects.Modules.Module.Module):
	
	def __init__(self):
		super(Scanner, self).__init__()

		self.LoggingPrefix = "Scanner"
		self.Radius = 3
		self.FoundObjects = False

		self.FoundObjects = {}

		self.CommandRoutingTable['List'] = "ProcessListScannedObjects"

	def Tick(self):
		super(Scanner, self).Tick()
		
		self.InternalScan()

	def ProcessListScannedObjects(self, TheCommand):
		Buffer = ""
		for GOBID in self.FoundObjects:
			GOB = self.FoundObjects[GOBID]
			Buffer = Buffer + str(GOB.ID) + " - " + str(GOB.SeenAs) + "\n"

		return Buffer

	def InternalScan(self):
		# Todo - add some clean up support

		# Scanners only work when theya re in a ship
		ParentGOB = self.GetParentGOB()
		if (ParentGOB == False):
			return

		# Just in case, other code should always ensure that the parent GOB (ie ship) will have a location		
		if (ParentGOB.MyLocation.ViewData == False):
			return

		# Loop through all the GOBIDs in the locations view and push them in
		# the Scanners Found objects Dict
		for GOBID in ParentGOB.MyLocation.ViewData:
			# check to see if the object has already been found, if so update the last time it has been seen			
			if (GOBID in self.FoundObjects):
				self.FoundObjects[GOBID].UpdateLastSeen()
			else:
				GOB = self.MyUniverse.GOBID(GOBID)
				if (GOB is False):
					continue
				else:
					NewScannedObject = ScannedObject(GOBID, GOB.ScanMe())
					self.FoundObjects[GOBID] = NewScannedObject		

class ScannedObject(Base.Base):
	def __init__(self, ID, SeenAs):
		super(ScannedObject, self).__init__()

		self.ID = ID
		self.SeenAs = str(SeenAs)

	def UpdateLastSeen(self):
		pass











