import sys

# for 2.x this class must be derived from "object"
class Base(object):
	
	def __init__(self):
		self.LoggingEnabled = True
		self.LoggingPrefix = "UnDefined"

	def FileGetContents(self, Path):
		File = open(Path,'r')
		Buffer = File.read()
		File.close()
		return Buffer

	def FilePutContents(self, Path, Buffer):
		File = open(Path,'w')
		File.write(Buffer)
		File.close()

	# ----------------------------------------
	# Factory
	def MillGameObjectHusk(self, Name):
		self.LogMe("Attempting to MillGameObjectHusk for -> " + Name)

		m = self.GetClass(Name)
		Object = m()
		return Object

	def GetClass(self, Name):
		parts = Name.split('.')
		module = ".".join(parts[:-1])
		m = __import__( module )
		for comp in parts[1:]:
			m = getattr(m, comp)

		return m

	# ----------------------------------------------------------------------
	# Logging
	def LogMe(self, Message):
		if (self.LoggingEnabled == True):
			Address = str(hex(id(self)))
			print( Address + " = " + self.LoggingPrefix + ": " + str(Message))
			# print str(Message)

	def Todo(self, Message):
		print ("X X -> Todo -> " + self.LoggingPrefix + " : " + str(Message))

	def Quit(self, Message):
		self.LogMe("!!!!! System will halt !!!!!!")
		sys.exit(Message)

	def Here(self, Message):
		self.LogMe("--- Here ---")
		sys.exit(Message)


	def DictToString(self, TheDict):
		Buffer = ""

		for Key in TheDict:
			KeyName = str(Key)
			ValueString =  str(TheDict[Key])
			Buffer = Buffer + KeyName + " = " + ValueString + "\n"

		return Buffer

	# ----------------------------------------------------------------------
	# Position Related
	def ComparePositions(self, Pos1, Pos2):
		if (Pos1['x'] != Pos2['x']):
			return False

		if (Pos1['y'] != Pos2['y']):
			return False

		if (Pos1['z'] != Pos2['z']):
			return False

		return True

	def PositionToString(self, Pos):
		Name = str(Pos['x']) + "@" + str(Pos['y']) + "@" + str(Pos['z'])
		return Name

	def StringToPosition(self, PosString):
		PosList = PosString.split("@")
		if (len(PosList) != 3):
			return False

		Pos = {}
		Pos['x'] = float(PosList[0])
		Pos['y'] = float(PosList[1])
		Pos['z'] = float(PosList[2])
		return Pos

	# ----------------------------------------------------------------------
	# Generic String to Real Python Types
	def ConversionWithTypeMatch(self, Original, New):

		# self.LogMe(" XX - > New = " + str(New))

		# this method assumes that a string will be passed

		# Default will assume fail
		Returned = {"Outcome": False, "Value": 0}

		# Handle Bool
		if ((Original is True) or (Original is False)):
			# self.LogMe(" XX - > Got Bool")
			if (New == "True"):
				# self.LogMe(" XX   - > Got True")
				Returned["Outcome"] = True
				Returned["Value"] = True
				return Returned

			elif (New == "False"):
				# self.LogMe(" XX   - > Got False")
				Returned["Outcome"] = True
				Returned["Value"] = False
				return Returned
			else:
				# self.LogMe(" XX   - > Got ???")
				# Default will be a fail
				return Returned

		# Handle Int
		elif (isinstance(Original, int) == True):
			# self.LogMe(" XX - > Got Int")
			try:
				Returned["Outcome"] = True
				Returned["Value"] = int(New)
				return Returned
			except:
				# Default will be a fail
				return Returned

		# Handle Float
		elif (isinstance(Original, float) == True):
			# self.LogMe(" XX - > Got Float")
			try:
				Returned["Outcome"] = True
				Returned["Value"] = float(New)
				return Returned
			except:
				# Default will be a fail
				return Returned

		# Handle String
		elif (isinstance(Original, str) == True):
			# self.LogMe(" XX - > Got Got String")
			try:
				Returned["Outcome"] = True
				Returned["Value"] = str(New)
				return Returned
			except:
				# Default will be a fail
				return Returned

		# Handle wtf, we have left overs
		else:
			return Returned