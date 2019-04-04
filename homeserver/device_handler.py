
#from homeserver.server_config import read_device_config
from homeserver.interface import DeviceInterface
from homeserver.voice_control.voice_controller import VoiceCommand
from homeserver import logger

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

	def get_status_json(self):
		"""
			return the current state of interfaces and devices.
			Returns a dictionary of 
			{
				'data':{
					'interfaces':{
						'interface1':{
							'name': string,
							'dev_id': string,
							'connected': bool
							'is_on': bool,
							'devices':{
								'device1':{
									'is_on':bool,
									'enabled': bool,
									'nice_name': string,
									'full_name': string,
									'location': string,
									'dev_id': string
								},
								'device2': {} ...
							}
						},
						'interface2': {} ...
					}
				}
	
			}
		"""


		data = dict()
		interfaces_dict = dict()

		for interface in self._interfaces:

			if_dict = dict()
			if_dict['name'] = interface.name
			if_dict['dev_id'] = interface.dev_id
			if_dict['connected'] = interface.connected
			if_dict['is_on'] = interface.is_on	

			devices_dict = dict()
			for device in interface.devices:

				d_dict = dict()				
				d_dict['is_on'] = device.is_on
				d_dict['enabled'] = device.enabled
				d_dict['nice_name'] = device.nice_name
				d_dict['full_name'] = device.full_name
				d_dict['location'] = device.location
				d_dict['dev_id'] = device.dev_id

				devices_dict[device.dev_id] = d_dict

			if_dict['devices'] = devices_dict
			interfaces_dict[interface.dev_id] = if_dict

		data['interfaces'] = interfaces_dict

		return data			



	def get_interface(self,interface_id):
		"""
			Returns the interface with the argument id
			or None if no interface is found
			params: 
				interface_id: string			

			return: 
				DeviceInterface
		"""

		for interface in self._interfaces:

			if interface.dev_id == int(interface_id):
				print("returning interface")
				return interface
		
		return None

	def get_device(self, device_id, interface_id):

		"""
			Returns the device with the argument id
			and interface_id 
			or None if no such id combination is found

			params: 
				device_id: string
				interface_id: string	

			return: (DeviceInterface, Device)		
		"""

		for interface in self._interfaces:
			if interface.dev_id == int(interface_id):					
				for device in interface.devices:
					if device.dev_id == int(device_id):
						return interface, device

		return None,None


	def handle_action(self, interface_id, action_name, device_id=None):
		"""
			params: 	@device_id: string
						@action_name: string, formatted as 
										name_param1_param2
						args is a list of strings
			return:		device if the handling was successful
								else None
		"""

		interface = None
		device = None

		if device_id is not None:		
			interface, device = self.get_device(device_id, interface_id)
		else:
			interface = self.get_interface(interface_id)

		if interface is None:
			logger.info("No interface with id {} found".format(interface_id))
			return 

		# get a target for the command
		target = interface.get_random_target()

		# create a command 
		command = VoiceCommand.command_from_api(target, action_name)

		logger.info("forwarding command: {}".format(command))

		# delegate the command to the interface
		interface.command_subjects(command)


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















	