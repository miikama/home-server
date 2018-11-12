
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
		self._interfaces = [];

		self.device_folder = folder

		self.read_devices()

		self.active_device = None

	@property
	def devices(self):
		""" Some devices have interfaces (such as philips lamps),
			which control multiple different devices. Interface is used 
			to get devices of the same type. This property is used
			 to hide this and return individual device objects
		"""
		devices = []

		for interface in self._interfaces:
			devices.append(interface)

		return devices


	def get_device(self,deviceId):

		for device in self._interfaces:
			if device.id == deviceId:
				return device

		return None

	def handle_action(self, device_id, action_name):
		"""
			@params: 	@device_id: string
						@action_name: string, formatted as 
										name_param1_param2
			@return:	device if the handling was successful
								else None
		"""
		device = self.get_device(device_id)

		if device:
			# pass the possible action to the device
			if device.perform_action(action_name):
				return device

		return None

	def handle_voice_command(self, vcommand):

		"""go through devices, if device.command has this 

		"""		
		#give the command to the active device
		if not vcommand.target and self.active_device:
			#TODO
			pass

		if len(vcommand.arguments) == 0:
			print("no arguments coming with the voice command")
			return

		action = vcommand.arguments[0]


		for device in self._devices:			
			#device has this command
			if device.target == vcommand.target:

				for command in device.commands:

					if action == command['action']:
						print("performing ", vcommand.target, " ", action , 
							"\nfor device ", device)

						command['action_func']()

	
	def read_devices(self):
		"""read the device configs in device_folder"""

		files = os.listdir(self.device_folder);

		for file in files:

			interface = DeviceInterface.intialize_device_interface(os.path.join(self.device_folder, file))

			if interface:
				self._interfaces.append(interface)


		logging.debug("interfaces: {}".format(self._interfaces))


	