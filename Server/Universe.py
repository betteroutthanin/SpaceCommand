import collections
import math
import time
import glob
import operator
import datetime

import Config
import Base
import Connect
import GameObjects.Ships.Ship 	# Needs to be included

class Universe(Base.Base):

	def __init__(self):
		super(Universe, self).__init__()
		
		self.LoggingEnabled = False
		self.LoggingPrefix = "Universe"
		
		# The master Game Object Bucket
		self.MasterObjects = {}
		
		# Ship Dict = ID -> ID
		self.Ships = {}

		# Location Bucket = X@Y@Z -> Location Object
		self.Locations = {}

		# ID stuff
		self.NextID = 0
		self.IDGaps = []

		# Global Matrix for high speed searches
		self.ViewSearchMatrix = False

	def Boot(self):
		self.LogMe("Attempting to start Sever")
		self.TheConnectionManager = Connect.ConnectionManager()
		self.TheConnectionManager.TheUniverse = self
		self.TheConnectionManager.Boot()
		self.LoadAllGameObjectsFromDisk()
		self.BuildViewMatrix()
		self.LogMe("Server Booted")

	def TickLoop(self):
		while(1):
			# Snap Shot of Time
			StartTime = datetime.datetime.now()

			self.LogMe("Universe Tick")

			# Get the locations to update their views
			self.TickLoopLocation()

			# Tick the ships
			self.TickLoopShip()

			# Tick the Connection Manager, do this last
			self.TheConnectionManager.poll()
			self.TheConnectionManager.ProcessConnections()

			# so sleepy
			EndTime = datetime.datetime.now()
			TimeDiff = EndTime - StartTime
			TimeDiffMS = TimeDiff.microseconds / 1000
			SleepTimeMS = Config.ServerFrameMS - TimeDiffMS
			if (SleepTimeMS < 0):
				SleepTimeMS = 0
			SleepTimeSec = SleepTimeMS / 1000.0
			time.sleep(SleepTimeSec)
			# self.LogMe("Sleep time = " + str(SleepTimeSec) + " | excution time MS = " + str(TimeDiffMS))
	# Tick all the ships and do there renders
	def TickLoopShip(self):
		for ShipId in self.Ships.keys():
			TheGameObject = self.GOBID(ShipId)
			TheGameObject.Tick()

	def TickLoopLocation(self):
		for LocationKey, LocationValue in self.Locations.iteritems():
			LocationValue.UpdateView()

	# ----------------------------------------
	# Layer 2 Routes

	# Pushes an object into space for the first time
	def VoidToSpace(self, TheGameObject):
		self.LogMe("Adding Game Object to space (MasterObjects) ID -> " + str(TheGameObject.ID))

		# All object go into the Master Game Object Dictionary.  It is assumed that that
		# the TheGameObject.ID is already an int
		self.MasterObjects[TheGameObject.ID] = TheGameObject

		# Each GameObject will need a link back to the Universe
		TheGameObject.MyUniverse = self

		# Ships need to be also added seperate List (only the ID)
		if isinstance(TheGameObject, GameObjects.Ships.Ship.Ship):
			self.LogMe("Got Ship, will be added to Ships Dict")
			self.Ships[TheGameObject.ID] = TheGameObject.ID
		else:
			self.LogMe("Game object is nothing special")

		# Finally the GOB will need to massaged into the location system.
		# This call is generally called when updating an GOB position
		self.ManageGameObjectLocationBucket(TheGameObject.ID)

	def SpaceToGob(self, ID, ParentID):
		self.LogMe("SpaceToGob ID = " + str(ID) + " : ParentID = " + str(ParentID))

		# Get the GOB from the MasterObjects so that we can set its OwnerID
		GOB = self.GOBID(ID)
		GOB.OwnerID = ParentID

		# Now pass the GOB ID to the parent GOB
		ParentGOB = self.GOBID(ParentID)
		Result = ParentGOB.AddChild(ID)

		# Remove the GOB from its location
		if (Result == True):
			GOB.MyLocation.RemoveGameObject(ID)


	# ----------------------------------------
	# GameObject Management

	# This function will pull all the objects from disk, populated them and
	# push them into space amd/or their parent objects.  Its big, fat and ugly
	def LoadAllGameObjectsFromDisk(self):
		self.LogMe("LoadAllGameObjectsFromDisk")
		# Game Objects exist on disk.  This this will loaded them in and populate husk
		# objects.  It will also manage the creation of the ID buffer.

		# GOBPreMasterDict is a dict within a dict
		# ID -> GameObjectData as dict (see line below)
		#		Label -> Value
		GOBPreMasterDict = collections.OrderedDict()

		# Get a file list of all the GOBs (Game Objects)
		GOBFileList = glob.glob(Config.GOBpath + "*.gob")

		# Parse each file and create a GOBDict for each.  In turn
		# each GOBDict will need to be added to the GOBPreMasterDict.
		# The GOBPreMasterDict will be unrolled to build all of the objects
		# in the universe but is also used to  to help build the ID system
		for GOBFileName in GOBFileList:
			# Convert the file into a dict so that is can be used by other parts
			# of the code
			GOBDict = self.ReadGOBFileIntoDict(GOBFileName)

			# The GOB dict must contain and ID, this is a minium.
			# Forcing this to be int an int now is important.  This is due to the
			# fact that all the ID related interations are based on int's
			GOBID = int(GOBDict['ID'])
			GOBPreMasterDict[GOBID] = GOBDict

		# Some objects will need to added to their parents.  This will be done in
		# a second pass but the data is build in the first pass.  It will be easier
		# if these objects are pushed into another list
		GOBSWithParents = {}

		# First pass loop(create and populate)
		for GOBDictID in GOBPreMasterDict:
			# GOBDict will be the Game Object Data this is used in this pass
			GOBDict = GOBPreMasterDict[GOBDictID]

			self.LogMe("First Loop Processing for " + GOBDict['Type'])

			# Create the object so that it can be populated
			TempGOB = self.MillGameObjectHusk(GOBDict['Type'])

			# Two tasks must be done before the auto populate can happen.
			# Firslt, force the ID to be an int.  All ID related tasks must be int's
			# Secondly set the Pos now and not at a lower layer.
			TempGOB.ID = int(GOBDict['ID'])
			TempGOB.Pos = TempGOB.StringToPosition(GOBDict['Pos'])

			# Before we call the PopulateUsingDict we should remove all the data that
			# we don't want the PopulateUsingDict to set within the target GOB.
			del GOBDict['ID']
			del GOBDict['Pos']
			del GOBDict['Type']
			TempGOB.PopulateUsingDict(GOBDict)

			# Does this GOB have a parent, if so push them into the parent list.
			# These will still be pushed into the space, but will be taken from
			# space and put into the target.  Once again force any ID related
			# data to be an int
			GOBDict['OwnerID'] = int(GOBDict['OwnerID'])
			if (GOBDict['OwnerID'] != -1):
				# The GOB has a parent, they will be bound to their parents in
				# the second pass
				GOBSWithParents[GOBDictID] = GOBDict

			# All is done, push the GOB into space make note that we are passing
			# the GOB and not its ID.  This is one of the only times that we will
			# pass an actually Game Object
			self.VoidToSpace(TempGOB)

		# At this point all of the objects should be in space.  From this point on
		# we should only deal with ID and not the actually GOBs themselves

		# The Second Pass #
		# Time to shift the object that have parents into their parents.  Please
		# read some of the comments above.  This loop depends on the previous
		# loop for the actually creation of the GOBs.  So the GOB should be in
		# MasterObjects dict and available via the GOBID method.
		for GOBDictID in GOBSWithParents:
			# NOTE - at this point the GOB (as held by the MasterObjects) will not
			# actually have its OwnerID set, instead it will have the the default
			# of -1.  We must used the OwnerID defined in the GOBPreMasterDict
			OwnerID = int(GOBPreMasterDict[GOBDictID]['OwnerID'])
			self.SpaceToGob(GOBDictID, OwnerID)

		# All done and dusted
		# Use the GOBPreMasterDict to help build the ID system
		self.BuildIDSystem(GOBPreMasterDict)

	def ReadGOBFileIntoDict(self, Path):
		FileBuffer = self.FileGetContents(Path)
		GOBDict = {}

		FileAsLine = FileBuffer.split("\n")
		for Line in FileAsLine:
			LineArray = Line.split("=")
			# array must have two parts (Label = Value)
			if (len(LineArray) == 2):
				# well formed
				# The two parts will need to be cleaned up
				Label = LineArray[0].strip()
				Value = LineArray[1].strip()

				# Add them to the GOB Dict
				GOBDict[Label] = Value
			else:
				# Miss formed
				# todo - deal with miss formed files
				pass

		return GOBDict

	# Get GameObject (object) by ID
	def GOBID(self, ID):
		TheGameObject = False
		if (ID in self.MasterObjects):
			TheGameObject = self.MasterObjects[ID]
		else:
			self.LogMe("-X- Failed to get object by ID -> " + str(ID))

		return TheGameObject

	# ----------------------------------------
	# ID Management

	def AllocateGameObjectID(self):
		NewID = self.NextID
		self.NextID = self.NextID + 1
		return NewID

	def BuildIDSystem(self, GOBPreMasterDict):
		# We need to know the larget ID Key
		LargestID = 0
		for ID in GOBPreMasterDict:
			if (ID > LargestID):
				LargestID = ID

		# Loop and look for any missing ID
		for IDtoCheck in range(0, LargestID + 1):
			if ((IDtoCheck in GOBPreMasterDict) == False):
				self.IDGaps.append(IDtoCheck)

		self.NextID = LargestID + 1
		# self.LogMe("NextID = " + str(self.NextID))
		# self.LogMe("IDGaps = " + str(self.IDGaps))

	# ----------------------------------------
	# Location Management

	def ManageGameObjectLocationBucket(self, ID):

		TheGameObject = self.GOBID(ID)
		if (TheGameObject is False):
			self.Todo("ManageGameObjectLocationBucket -  find a better way to deal with this")
			return False

		self.LogMe("ManageGameObjectLocationBucket -> " + str(TheGameObject.ID))

		Pos = TheGameObject.GetPos()

		# Positions will contain an dictionary of floats.  This will need to be floored
		# todo - add some more detailed comments
		fPos = {}
		fPos['x'] = int(math.floor(Pos['x']))
		fPos['y'] = int(math.floor(Pos['y']))
		fPos['z'] = int(math.floor(Pos['z']))

		# Geneate a location string
		PositionString = self.PositionToString(fPos)

		# Does the location exist in the list
		if ((PositionString in self.Locations) == False):
			# Location was not found - create it
			self.Locations[PositionString] = Location(PositionString, self, fPos)
		else:
			self.LogMe("Location already exisits -> " + PositionString)

		# in theory this should never fail due to the fact that we are creating
		# any minssing Location of the code snippet above
		TargetLocation = self.Locations[PositionString]

		# The GameObject may already be at this location, if so then there is nothing to be done.
		# just return
		if (TargetLocation == TheGameObject.MyLocation):
			# Object is already here
			self.LogMe("GameObject already in target location, nothing to do " + PositionString)
			return

		# The GameObject is at the wrong location, remove it from its current and add it
		# to the new location.  But in some cases the object may not yet have a location.
		# if so then please just don't do the removeral part
		if (TheGameObject.MyLocation != False):
			# Time to remove the object from its current location
			TheGameObject.MyLocation.RemoveGameObject(TheGameObject.ID)
			# todo - Add some Garbage collection here

		# Add the object to a location
		TargetLocation.AddGameObject(TheGameObject.ID)
		self.LogMe("ManageGameObjectLocationBucket - Ended with Add")

	def GetLocationByPos(self, Pos):
		PosString = self.PositionToString(Pos)
		return self.GetLocationByString(PosString)

	def GetLocationByString(self, PosString):
		if PosString in self.Locations:
			return self.Locations[PosString]
		else:
			return False


	# One off run to build the search matrix
	def BuildViewMatrix(self):

		xc = 0
		yc = 0
		zc = 0

		Radius = Config.ViewRadius

		x1 = xc - Radius
		y1 = yc - Radius
		z1 = zc - Radius

		x2 = xc + Radius + 1
		y2 = yc + Radius + 1
		z2 = zc + Radius + 1

		Matrix = {}
		Sorter = {}

		IndexCount = 0

		# Build
		for z in range(z1, z2):
			for y in range(y1, y2):
				for x in range(x1, x2):
					Pos = {"x":x, "y":y, "z":z}

					Diff = {}
					Diff['x'] = Pos['x'] - xc
					Diff['y'] = Pos['y'] - yc
					Diff['z'] = Pos['z'] - zc
					Distance = math.sqrt((Diff['x']**2) + (Diff['y']**2) + (Diff['z']**2))

					Entry = {}
					Entry['Pos'] = Pos
					Entry['Distance'] = Distance
					Matrix[IndexCount] = Entry
					Sorter[IndexCount] = Entry['Distance']

					IndexCount = IndexCount + 1

		# Sort
		sorted_x = sorted(Sorter.iteritems(), key=operator.itemgetter(1))
		FinalMatrix = []
		IndexCount = 0

		# Final Build
		for a in sorted_x:
			Index = a[0]
			# FinalMatix[IndexCount] = Matrix[Index]
			FinalMatrix.append(Matrix[Index])
			IndexCount = IndexCount + 1

		self.ViewSearchMatrix = FinalMatrix

	# ----------------------------------------
	# Server Remote Commands

	def RSC_KillServer(self):
		self.LogMe("RSC_KillServer")
		self.Quit("Server will die")

	def RSC_SaveAllGOBs(self):
		for ID in self.MasterObjects:
			GOB = self.GOBID(ID)
			GOB.SaveToDisk()

# ----------------------------------------
# The location class

class Location(Base.Base):
	
	def __init__(self, LocationName, TheUniverse, Pos):
		super(Location, self).__init__()

		self.LoggingPrefix = "Location"
		self.LoggingEnabled = True

		self.LocationName = LocationName
		self.LoggingPrefix = "Location " + self.LocationName
		self.TheUniverse = TheUniverse
		self.Pos = Pos

		self.ViewData = False

		self.LogMe("Location Created")

		self.GameObjects = {}

	def UpdateView(self):
		# self.LogMe("UpdateView")
		# self.LogMe("My Pos = " + str( self.Pos))

		Matix = self.TheUniverse.ViewSearchMatrix
		self.ViewData = {}

		for MatrixBlock in Matix:

			# ViewSearchMatrix will need to be mutliplied by the locations position.
			# Due to the fact that the ViewSearchMatrix is based on a 0,0,0 origon
			SearchPos = {}
			SearchPos['x'] = MatrixBlock['Pos']['x'] + self.Pos['x']
			SearchPos['y'] = MatrixBlock['Pos']['y'] + self.Pos['y']
			SearchPos['z'] = MatrixBlock['Pos']['z'] + self.Pos['z']

			# self.LogMe("Looking at " + str(SearchPos))

			LocationObject = self.TheUniverse.GetLocationByPos(SearchPos)
			if (LocationObject is False):
				# self.LogMe("Got Pos Failed")
				continue

			# self.LogMe("Got Pos")

			# else, we got a lock
			for GOBID in LocationObject.GameObjects:
				# self.LogMe("Got Object = " + str(GOBID))
				self.ViewData[GOBID] = GOBID

		# self.LogMe("View Data = " + str(self.ViewData))

	def RemoveGameObject(self, ID):

		TheGameObject = self.TheUniverse.GOBID(ID)
		if (TheGameObject is False):
			# todo - add better error handling
			return False

		self.LogMe("Removing game object from Location -> " + str(TheGameObject.ID))

		# tell the location to forget about the GameObject
		self.GameObjects.pop(TheGameObject.ID)

		# todo - ask the location of that is the last one, if so
		# then destroy the location and remove if from the grid

		# tell the object to forget about the location
		TheGameObject.MyLocation = False

		# wow danger.  The object doesn't have a location

	def AddGameObject(self, ID):
		TheGameObject = self.TheUniverse.GOBID(ID)
		if (TheGameObject is False):
			# todo - add better error handling
			return False

		self.LogMe("Adding game object to Location -> " + str(TheGameObject.ID))
		TheGameObject.MyLocation = self
		self.GameObjects[TheGameObject.ID] = TheGameObject.ID

	def Dump(self):
		self.LogMe("Dump of GameObjects\n" + self.DictToString(self.GameObjects))