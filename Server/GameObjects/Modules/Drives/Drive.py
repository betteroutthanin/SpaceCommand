import math

import Config
import GameObjects.Modules.Module

class Drive(GameObjects.Modules.Module.Module):

	def __init__(self):
		super(Drive, self).__init__()

		self.LoggingEnabled = False
		self.LoggingPrefix = "Drive"

		# Some Drive Defaults
		self.Destination = "0@0@0"
		self.Active = False
		self.SubLightLMS = 500000.0 / Config.LightMinuteInKm		# make note of the forced floats
		self.JumpDistanceLM = 10
		self.AutoJumpThresholdLM = 15
		self.JumpDriveChargeRateS = 15
		self.CurrentDriveCharge = Config.JumpDriveUpperCharge

		## Save List
		self.SaveList.append("Destination")
		self.SaveList.append("Active")

		## Getters and Setters
		# Where we are going
		self.GetAbleList.append("Destination");
		self.SetAbleList.append("Destination");

		# Active ?
		self.GetAbleList.append("Active");
		self.SetAbleList.append("Active");

		# General Status on the drive
		self.GetAbleList.append("SpeedKms");
		self.GetAbleList.append("JumpDistanceLM");
		self.GetAbleList.append("JumpDriveChargeRateS");
		self.GetAbleList.append("AutoJumpThresholdLM");
		self.GetAbleList.append("CurrentDriveCharge");

		# Distance to a point in space
		self.CommandRoutingTable['distanceto'] = "ProcessDistanceToPoint"

	def Tick(self):
		super(Drive, self).Tick()
		self.LogMe("Tick Starting")
		self.Tick_MoveShip()
		self.LogMe("Tick complete")

		# self.LogMe("Destination = " + self.Destination)

	def Tick_MoveShip(self):

		# Ship ID is needed for the triggering of the events.  Ensure the drive is in
		# a ship will ensure that drive can't just jump
		ShipID = self.OwnerID
		if (ShipID == -1):
			# Todo - add some better error handling - drive doesn't have a prarent
			return

		ShipGameObject = self.MyUniverse.GOBID(ShipID)
		if (ShipGameObject == False):
			# todo - failed to get the ship game object
			return

		# At this point we have a valid ship game object (the drive's parent)
		self.LogMe("#########################################")
		# Get the Source and Destination as 3 Part Dicts (x, y, z).  The position will be extracted
		# from the drive, but the drive will reference the parents (ship) position instead via the
		# GetPos function
		S = self.GetPos()
		D = self.StringToPosition(self.Destination)
		self.LogMe(" Start = " + str(S))
		self.LogMe(" Dest  = " + str(D))

		# Has the ship reached its destination, if so, do the following
		# - disable the drives
		# - send an event to code
		if (self.ComparePositions(S, D) == True):
			# Only do the following of the drive was active, not doing this
			# will create a lot of spam messages.  No need to return out of this
			# this is due the fact that the Active state of False will pop the drive
			# out of what it is doing
			if (self.Active == True):
				self.Active = False
				self.LogMe(" Drive did arrive")

				# Todo - work ut event system
				EventString = "Drive:Destination Reached:" + str(self.Destination)
				ShipGameObject.TriggerEvent(EventString)

		# The drive will recharge after a jump.  The drive should stop
		# charing when it hits the max.  Charge rate are define in per second
		# unit so please ensure it is reduced to match server frame rate.
		# A recharging can do no other thing until it is recharged
		if (self.CurrentDriveCharge < Config.JumpDriveUpperCharge):
			Charge = self.JumpDriveChargeRateS * Config.FrameMultiSec
			self.CurrentDriveCharge = self.CurrentDriveCharge + Charge
			self.LogMe("CurrentDriveCharge = " + str(self.CurrentDriveCharge))
			if (self.CurrentDriveCharge >= Config.JumpDriveUpperCharge):
				# Engine has completely charged
				self.CurrentDriveCharge = Config.JumpDriveUpperCharge
				self.LogMe("Engine has charged")
			else:
				# Drive is still charging, jump out
				return

		# Don't need to act if the drive is off (or not active)
		if (self.Active is False):
			return

		# Time to Move
		Distance = {}
		Distance['x'] = D['x'] - S['x']
		Distance['y'] = D['y'] - S['y']
		Distance['z'] = D['z'] - S['z']
		self.LogMe("Distance = " + str(Distance))

		# Work out how far the dest is in LM
		TotalDist = math.sqrt((Distance['x'] ** 2) + (Distance['y'] ** 2) + (Distance['z'] ** 2))
		self.LogMe("TotalDist = " + str(TotalDist))

		# The drive will need to determine weather to use sub light or jump drive.
		# THe Jump Threshold is the drive key indicator of this.
		TravelDistance = 0

		self.LogMe("JumpDistanceLM = " + str(self.JumpDistanceLM))
		self.LogMe("AutoJumpThresholdLM = " + str(self.AutoJumpThresholdLM))
		self.LogMe("SubLightLMS = " + str(self.SubLightLMS))

		if (TotalDist > self.AutoJumpThresholdLM):
			TravelDistance = self.JumpDistanceLM
			# the ship will jump, so CurrentDriveCharge must be set to 0
			# to emulate the jump, this will force the drive to charge over time
			self.LogMe("Ship is jumping !!!!!")
			self.CurrentDriveCharge = 0
		else:
			# Ship will need to use SubLight engines, make sure it ends up as SU
			# and scaled to match FPS
			self.LogMe("Ship is using sub light drives LMpS = " + str(self.SubLightLMS))
			TravelDistance = self.SubLightLMS * Config.FrameMultiSec

		# If the travel distance is less then the total distance then just
		# set the ships position to that of the dest.  This will help with
		# crappy rounding issues
		if (TravelDistance > TotalDist):
			self.LogMe("Drive will now update the ships position !!!!!")
			self.SetPos(D)
			return

		self.LogMe("Tavel Distance for this frame in SU = " + str(TravelDistance))

		# Work out far the ship will travel from the origin 0 0 0
		TravelDistFromOrig = {}
		TravelDistFromOrig['x'] = (Distance['x'] / TotalDist) * TravelDistance
		TravelDistFromOrig['y'] = (Distance['y'] / TotalDist) * TravelDistance
		TravelDistFromOrig['z'] = (Distance['z'] / TotalDist) * TravelDistance
		self.LogMe("TravelDistFromOrig = " + str(TravelDistFromOrig))

		NewPos = {}
		NewPos['x'] = S['x'] + TravelDistFromOrig['x']
		NewPos['y'] = S['y'] + TravelDistFromOrig['y']
		NewPos['z'] = S['z'] + TravelDistFromOrig['z']

		# Update the drives postion, this inturn should set the postion of the
		# ship via the SetPos function
		self.LogMe("Drive will now update the ships position")
		self.SetPos(NewPos)

	# --------------------------------------
	#   Module Command Processing
	# --------------------------------------

	def ProcessDistanceToPoint(self, TheCommand):

		# todo - fix this
		DestStr = TheCommand.Parm[0]
		Dest = self.DestStrToDest(DestStr)

		if (Dest is False):
			return "Command Failed: Can't convert position string to space cords -> " + str(DestStr)

		x1 = self.ShipObject.Pos['x']
		y1 = self.ShipObject.Pos['y']
		z1 = self.ShipObject.Pos['z']

		x2 = Dest['x']
		y2 = Dest['y']
		z2 = Dest['z']

		Dist = math.sqrt(((x1-x2)**2)+((y1-y2)**2)+((z1-z2)**2))

		return Dist