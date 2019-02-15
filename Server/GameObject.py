import Base
import Config

class GameObject(Base.Base):	

	def __init__(self):
		super(GameObject, self).__init__()
		
		self.LoggingPrefix = "Game Object"
		self.LoggingEnabled = False

		# Relationship with Parent/Owner
		# ID of -1 means no owner, free floating
		self.OwnerID = -1
		self.OwnerMarker = 0		

		# ZOB id, -1 means invalid
		self.ID = -1
		
		# Position in space and relationship to locations
		self.Pos = {'x':0, 'y':0, 'z':0}
		self.MyLocation = False
		self.MyUniverse = False
		
		# Objects can have children (this will be a dict)
		self.Children = {}

		# What do we need to save
		self.SaveList = []
		self.SaveList.append("ID")
		self.SaveList.append("OwnerID")
		self.SaveList.append("OwnerMarker")

		self.LogMe("Object Created")

	def GetParentGOB(self):
		# Make sure we pass an int, if not we need to crack the shits
		if (isinstance( self.OwnerID, int ) == False):
			self.LogMe("Crack self.OwnerID is not an int")

		self.LogMe("GetParentGOB OwnerID-> " + str(self.OwnerID))
		if (self.OwnerID == -1):
			return False

		ParentGOB = self.MyUniverse.GOBID(self.OwnerID)
		self.LogMe("GetParentGOB Parent Found -> " + str(self.OwnerID))

		return ParentGOB

	def LogMe(self, Message):
		if self.ID is False:
			IDstr = "<No ID>"
		else:
			IDstr = "ID="+str(self.ID)

		NewMessage = IDstr + ": " + Message
		super(GameObject, self).LogMe(NewMessage)

	def SaveToDisk(self):
		# FileName
		Number = str(self.ID)
		FileName = Number.rjust(10, '0') + ".gob"

		self.LogMe("FileName = " + FileName)

		# Clear the buffer
		Buffer = ""

		# Type first
		Buffer = Buffer + "Type" + " = " + self.__module__ + "." + self.__class__.__name__ + "\n"

		# Position next
		Buffer = Buffer + "Pos" + " = " + self.PositionToString(self.Pos) + "\n"

		# Loop and build the Buffer
		for ValueName in self.SaveList:
			Value = str(getattr(self, ValueName))
			Buffer = Buffer + ValueName + " = " + Value + "\n"

		# Save the buffer to the file
		self.FilePutContents(Config.GOBpath + FileName, Buffer)

	# ----------------------------------------
	# Position Related
	def GetPos(self):
		self.LogMe("Getting Pos")
		# Some Gobs have parents.  In this case get the pos of the parent instead
		ParentGOB = self.GetParentGOB()
		if (ParentGOB is False):
			# What, no parent, return you own Pos
			return self.Pos
		# else
		# Ok we have a parent, return the parents GOBs Pos
		return ParentGOB.GetPos()

	def SetPos(self, Pos):
		self.LogMe("Attempting to run Setting Pos")
		# Some Gobs have parents.  In this case set the pos of the parent instead
		ParentGOB = self.GetParentGOB()
		if (ParentGOB is False):
			# What, no parent
			self.LogMe("Setting Pos -> Self - I am the parent")
			self.Pos = Pos
			self.MyUniverse.ManageGameObjectLocationBucket(self.ID)
			return

		self.LogMe("SetPos parent Gob = " + str(ParentGOB))
		self.LogMe("SetPos My Parent ID = " + str(self.OwnerID))

		# else
		# Ok, we have a prarent, set the parents GOBs Pos
		ParentGOB.SetPos(Pos)

	# ----------------------------------------
	# DB and Population
	def PopulateUsingDict(self, DataDict):
		for Key in DataDict:
			OriginalValue = getattr(self, Key)
			NewValue = DataDict[Key]

			Result = self.ConversionWithTypeMatch(OriginalValue, NewValue)
			ConvertedValue = Result['Value']
			Outcome = Result['Outcome']

			setattr(self, Key, ConvertedValue)

	# ----------------------------------------
	# Defaults
	def IsMineable(self):
		return False

	def ScanMe(self):
		return str(self.__class__.__name__)

	# ----------------------------------------
	# Fall through catchers
	def CheckPassWord(self, PasswordToCheck):
		return False

	def SetConnection(self, Connection):
		pass

	def Tick(self):
		pass

	def AddChild(self, ChildID):
		pass

