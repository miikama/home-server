
from server_config import read_device_config

import os



class DeviceHandler():
	'''
	Class for interacting with devices
	'''

	# list of all the device objects
	devices = [];



	def __init__(self, folder):
		"""is given the folder of the device_configs as parameter"""
		

		self.device_folder = folder

		self.read_devices()


	def get_device(self,deviceId):

		for device in self.devices:
			if device.id == deviceId:
				return device

		return None

	def handle_action(self, device_id, action_name):
		"""
			@params: 	@device_id: string
						@action_name: string, formatted as 
										name_param1_param2
			@return:	boolean, was the handling successful
		"""
		device = self.get_device(device_id)

		if device:
			# pass the possible action to the device
			if device.perform_action(action_name):
				return device

		return None

	
	def read_devices(self):
		"""read the device configs in device_folder"""

		files = os.listdir(self.device_folder);

		for file in files:

			device = read_device_config(os.path.join(self.device_folder, file))

			if device:
				self.devices.append(device)


		print("devices: ", self.devices)


	