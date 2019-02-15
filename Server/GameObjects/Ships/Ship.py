import Base
import GameObject

class Ship(GameObject.GameObject):

	def __init__(self):
		super(Ship, self).__init__()

		self.LoggingPrefix = "Ship"
		self.LoggingEnabled = False

		# Ships have modules, which are mapped to GameObjects Children

	def Tick(self):
		super(Ship, self).Tick()

		self.LogMe("Start ing the module loop")
		# Work through the slots and see if there is gettable objects in them
		for SlotID in self.Children:
			GameObjectID = self.Children[SlotID].GameObjectID
			if (GameObjectID >= 0):
				TheGameObject = self.MyUniverse.GOBID(GameObjectID)
				TheGameObject.Tick()

		self.LogMe("Tick complete")

	def TriggerEvent(self, EventString):
		# NOTE, below code assues that the computer will always be in slot x
		ComputerSlot = 1

		ComputerObjectID = self.Children[ComputerSlot].GameObjectID
		if (ComputerObjectID == -1):
			# Todo - add some better error handling
			return

		ComputerObject = self.MyUniverse.GOBID(ComputerObjectID)
		if (ComputerObject is False):
			# Todo - add some better error handling
			return

		FinalEventString = "Event:" + EventString
		ComputerObject.AddEvent(FinalEventString)

	def CreateModuleSlot(self, Type, MaxClass):
		return ModuleSlot(Type, MaxClass, self)

	def GenerateModuleListAsString(self):

		Buffer = ""

		for SlotID in self.Children:
			SlotIDString = str(SlotID)
			ValueString = str(self.Children[SlotID].GetCurrentSlotInfo())
			Buffer = Buffer + SlotIDString + " = " + ValueString + "\n"

		return Buffer

	def AddChild(self, ChildID):
		# We assume that the child has the OwnerMarker Set
		return self.AddGameObectToSlot(ChildID)

	def AddGameObectToSlot(self, ID):
		# Make sure the object exists
		TheGameObject = self.MyUniverse.GOBID(ID)
		if (TheGameObject is False):
			self.LogMe("Failed to get object -> " + str(ID))
			return False

		# Extract the SlotID from the Object that is to be added
		SlotID = TheGameObject.OwnerMarker

		# Does the slot exits
		if ((SlotID in self.Children) == False ):
			self.LogMe("Slot does not exist")
			return False

		# is the slot empty?
		if (self.Children[SlotID].HasObject() == True):
			self.LogMe("Slot is not empty")
			return False

		# Try to add the object (by ID)
		Outcome = self.Children[SlotID].AddGameObectToSlot(TheGameObject)

		# All Good, since the ship now is the owner of the Module the modules
		# owner ID should be updated to reflect this.  This may already be done
		# but it is better to do it just incase
		if (Outcome == True):
			TheGameObject.OwnerID = self.ID

		return Outcome

class ModuleSlot(Base.Base):	

	def __init__(self, Type, MaxClass, ShipObject):
		super(ModuleSlot, self).__init__()

		self.LoggingPrefix = "ModuleSlot"
		self.LoggingEnabled = True

		self.ShipObject = ShipObject
		self.Type = Type
		self.MaxClass = MaxClass
		self.GameObjectID = -1
		self.LogMe("Created, " + str(Type) + " ," + str(MaxClass))

	# Adds a existing GOB to the slot
	def AddGameObectToSlot(self, TheGameObject):
		# !!! We must pass the actual object to this function, this is
		# due to the fact the the ModuleSlot class has no visabilty of
		# the Universe (which is needed to resolve IDs into GameObjects).
		# The Universe link is borrowed from the passed GOB

		# The GameObject must be of the type defined by the slot
		ReferenceObject = self.GetClass(self.Type)
		if (isinstance(TheGameObject, ReferenceObject) == False):
			self.LogMe("Module being added did not match type define for slot -> " +  str(self.Type))
			return False

		# The Game Object must be equal or less than the defined class
		if (TheGameObject.Class > self.MaxClass):
			self.LogMe("Slot can't take object of that class number")
			return False

		# All conditions met, time to add
		self.GameObjectID = TheGameObject.ID
		self.LogMe("GameObject added to slot -> " + str(self.GameObjectID))

		return True

	# Returns a class name of the GOB in the slot
	def GetCurrentSlotInfo(self):
		if (self.GameObjectID == -1):
			return "Empty"

		# Get the object in the slot and work out what type it is
		TargetGameObject = self.ShipObject.MyUniverse.GOBID(self.GameObjectID)
		if (TargetGameObject is False):
			return "Empty"

		return str(TargetGameObject.__class__.__name__)

	# Checks to see if the slot object has an object	
	def HasObject(self):
		if(self.GameObjectID == -1):
			return False

		# else, the slot has an object
		return True