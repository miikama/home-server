

from homeserver import logger


class DeviceCommand():

	"""a class encapsulating the voice commands


		Possible interfaces:
			PhilipsLamp:
				targets:  "valot", "philips_light"

				commands: "päälle", "pois", "alas", "ylös"

			SamsungTV:
				targets: "tv", "samsung_tv"
		
				commands: "päälle", "pois"

	"""

	def __init__(self, target=None,arguments=[] ):
		"""
		@params: target: string, the device/thing affected
				arguments: list of strings of that determine 
				what should the device/thing in question do
		 """
		if target is not None:	 		
			self.target	= target.lower()
		else:
			self.target = target

		self.arguments = arguments
		for i in range(len(self.arguments)):
			self.arguments[i] = self.arguments[i].lower()

	@classmethod
	def command_from_string(cls, command_string ):
		"""
		a class constructor to create a new Devicecommand from a string

		if the command string only has one word, it is interpreted 
		as a command to the active device, and the target of the command 
		is left as None

		This method is thought to be used to create a command from
		detected speech.

		"""
		splitted = command_string.split(' ')

		if len(splitted) == 1:
			return cls( arguments=splitted )

		else:
			target = splitted[0]
			args = splitted[1:]
			return cls(target=target, arguments=args)


	@classmethod
	def command_from_api(cls, target, command_name):
		"""
			This method creates a command for the devices from based on the given
			arguments. 

			Mainly be used from the web api

		"""
		logger.info("creating command from api with target {} and command {}".format(target, command_name))

		return cls(target=target, arguments=[command_name])


	def __repr__(self):
		return "DeviceCommand on target {} with arguments: {}".format(self.target, self.arguments)

