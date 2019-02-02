
#from homeserver.server_config import read_device_config
from homeserver.device import DeviceInterface

import os
import logging






class DeviceHandler():
	'''
	Class for interacting with devices
	'''


	def __init__(self, folder):
		"""is given the folder of the device_configs as parameter"""
		
		# list of all the device objects
		self._interfaces = []

		#folder where all the device configs live
		self.device_folder = folder

		self.read_devices()

		self.active_device = None

	@property
	def interfaces(self):
		""""""
		return self._interfaces

	def add_interface(self, interface):
		self._interfaces.append(interface)


	@property
	def devices(self):
		"""
			Some devices have interfaces (such as philips lamps),
			which control multiple different devices. Interface is used 
			to get devices of the same type. This property is used
			to hide this and return individual device objects
		"""
		devices = []

		for interface in self._interfaces:
			devices_list = interface.devices
			for device in devices_list:
				devices.append(device)

		return devices

	def get_interface(self,device_id):
		"""
			First go through the interfaces and devices within and command the interface
			which has the argument id.
			Returns the interface where the argument id is in
			Finally if no device with id found return None.
		"""
		for interface in self._interfaces:
			if interface.dev_id == device_id:
				return interface
			for device in interface.devices:
				if device.dev_id == device_id:
					return interface

		return None

	def handle_action(self, device_id, action_name, args=[]):
		"""
			@params: 	@device_id: string
						@action_name: string, formatted as 
										name_param1_param2
						args is a list of strings
			@return:	device if the handling was successful
								else None
		"""
		interface = self.get_device(device_id)

		if interface:
			if action_name == "is_on":
				if args[0] == "True":					
					interface.toggle_on()
				else:
					interface.toggle_off()
			

		return None

	def handle_voice_command(self, vcommand):
		"""
			Check if the voice command target matches any device target
			go through devices, if device.command has this 

		"""		

		#give the command to the active device
		if not vcommand.target and self.active_device:
			#TODO
			pass

		if len(vcommand.arguments) == 0:
			print("no arguments coming with the voice command")
			return

		for interface in self._interfaces:			
			#device has this command
			if interface.target in vcommand.targets:
				interface.command_subjects(vcommand)
				

	def get_voice_keys(self):
		"""
			Returns the keywords for the voice commands as list of strings,
			used as keywords for the google speech to text api
		"""
		keywords = []
		for interface in self._interfaces:
			keywords.append(interface.get_voice_keywords())
		flatlist = [word for keys in keywords for word in keys ]
		return flatlist # list of strings

	
	def read_devices(self):
		"""read the device configs in device_folder"""

		files = os.listdir(self.device_folder);

		for file in files:

			interface = DeviceInterface.intialize_device_interface(os.path.join(self.device_folder, file))

			if interface:
				self._interfaces.append(interface)


		logging.debug("interfaces: {}".format(self._interfaces))










	