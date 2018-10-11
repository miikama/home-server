
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


	
	def read_devices(self):
		"""read the device configs in device_folder"""

		files = os.listdir(self.device_folder);

		for file in files:

			device = read_device_config(os.path.join(self.device_folder, file))

			if device:
				self.devices.append(device)


		print("devices: ", self.devices)


	