
#from homeserver.server_config import read_device_config
from homeserver.interface import DeviceInterface

import os
import logging






class DeviceHandler():
	'''
	Class for interacting with devices
	'''

	# static variable to count all initialized devices and interfaces 
	# use to give device ids
	counter = 0


	def __init__(self, folder):
		"""is given the folder of the device_configs as parameter"""
		
		# list of all the device objects
		self._interfaces = []

		#folder where all the device configs live
		self.device_folder = folder

		interfaces = self.read_devices()
		#register the interfaces
		self.register_interfaces(interfaces)

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

		# go through each interface and check if the voicecommand target is 
		# in inteface targets
		for interface in self._interfaces:				
			
			if vcommand.target in interface.targets:
				#device has this command
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

		interfaces = []

		for file in files:

			interface = DeviceInterface.intialize_device_interface(self,os.path.join(self.device_folder, file))  

			if interface:
				interfaces.append(interface)


		logging.debug("Loaded interfaces: {}".format(self.interfaces))

		return interfaces

	def register_interfaces(self, interfaces):
		"""
		Register a list on interfaces
		Add a unique id to all of them and add to the 
		_interfaces dictionary: id: interface
		"""

		for interface in interfaces:

			# add to global counter
			DeviceHandler.counter += 1
			# add a unique dev_id also to the interface
			interface.dev_id = DeviceHandler.counter

			self._interfaces.append(interface)

	def register_device(self, device=None):
		"""return a unique device id """

		self.counter += 1

		return self.counter















	