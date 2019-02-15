import StateMachine

class Simple(StateMachine.StateMachine):

	def __init__(self):
		super(Simple, self).__init__()

		self.Options["State_DoStuff"] = self.State_DoStuff

		self.Options["State_Start"] 		= self.State_Start
		self.Options["State_InTransit"] 	= self.State_InTransit
		self.Options["State_Destination_1"] = self.State_Destination_1
		self.Options["State_Destination_2"] = self.State_Destination_2

		# Destination Reached
		self.AddEventHandler("Destination Reached", self.Handle_DestinationReached)

		self.DriveSlot = "0"
		self.DestID = 0

		self.DestNames = {}
		self.DestNames[0] = "2@2@2"
		self.DestNames[1] = "4@4@4"
		self.DestNames[2] = "6@4@4"
		self.DestNames[3] = "8@4@4"
		self.DestNames[4] = "10@4@4"


	def State_DoStuff(self):
		self.State = "State_Start"

	def State_Start(self):
		print("State_Start")
		self.State = "State_InTransit"
		Message = self.DriveSlot + ":Set Destination " + self.DestNames[self.DestID]
		self.SendMessage(Message)
		Message = self.DriveSlot + ":Set Active True"
		self.SendMessage(Message)

	def State_InTransit(self):
		pass

	def State_Destination_1(self):
		print("State_Destination_1")
		self.State = "State_Destination_2"

	def State_Destination_2(self):
		print("State_Destination_2")
		self.State = "State_Start"

	def Handle_DestinationReached(self, EventData):
		print str(EventData)
		self.State = "State_Start"
		self.DestID = self.DestID + 1
		if (self.DestID > 4):
				self.DestID = 0



