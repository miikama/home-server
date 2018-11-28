import logging
import configparser
import importlib
import time, os

from homeserver import app


from phue import Bridge, Light, PhueRegistrationException
import random

class DeviceCommand():

	def __init__(self,target, action, action_func):

		self.target_device = target
		self.action = action
		self.action_func = action_func



class DeviceInterface():
	"""
	A class that hides the fact that multiple devices are controlled by 
	a single control point
	"""

	_devices = []

	#2d array of [["valot", "päälle", func ] ]
	commands = []

	#used to give this device commands
	target = None

	def __init__(self, config):

		""" Loads a config file and uses the DEVICE_CLASS parameter of 
		the config file to instantiate a right device class

		The class initialized should match the one in the config		
		"""

		raise NotImplementedError("Abstract base class")


	@property
	def devices(self):
		return self._devices

	def command_subjects(self,vcommand):
		"""Abstract base method	"""
		return NotImplementedError("Abstract base class")


	@classmethod
	def devices_from_config(cls, config):
		"""Loads a config file and uses the DEVICE_CLASS parameter of 
		the config file to instantiate a right device class

		The class initialized should match the one in the config		
		"""

		raise NotImplementedError("Abstract base class")
		

	@staticmethod
	def intialize_device_interface(file_path):
		"""Initializes a correct type of interface
		"""

		logging.debug("loading devices from {}".format(file_path))
		config = configparser.ConfigParser()
		try:
			config.read(file_path)
		except Exception as e:
			return None
		

		logging.debug("loaded device interface config {}".format(config))

		#import the device classes with importlib
		DeviceInterfaceClass = getattr(importlib.import_module("homeserver.device"), config['DEFAULT']['DEVICE_CLASS'])

		return DeviceInterfaceClass(config)

		"""This phase is done for all different configs. After this 
		It depends on the device type, whether device_interface initializes multiple 
		device objects or 

		"""

	def get_voice_keywords(self):
		""" Returns list of strings """
		keywords = []
		if self.target:
			keywords.append(self.target)
		for command in self.commands:
			keywords.append(command.action)
		return keywords


	def perform_action(self, action_name):
		"""
		this function will be given an action_name as parameter, it will check if such an action exists
		@params: @action_name: str, formatted as name_param1_param2
		"""
		#do the trimming
		trimmed =action_name.split('_') 
		acname = trimmed[0]
		params = []
		if len(trimmed) > 1:
			params = trimmed[1:]


		try:
			method_to_call = getattr(self, acname)
			return method_to_call(*params)
			
		except Exception as e:
			raise e





class PhilipsLampInterface(DeviceInterface):
	
	def __init__(self, config):

		"""The class initialized should match the one in the 
			config
		"""
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not this class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))

		self.config = config
		
		self.bridge = self.connect_to_hue_bridge(config)

		self.target = "valot"

		self.commands = [ DeviceCommand(self.target, "päälle", self.toggle_on),
							DeviceCommand(self.target, "pois", self.toggle_off),
							DeviceCommand(self.target, "alas", self.dim_lights),
							DeviceCommand(self.target, "ylös", self.brighten_lights)]


		self.bridge_id = int(config['DEFAULT']['DEVICE_ID'])

	def connect_to_hue_bridge(self, config):
		"""
		function to establish a connection to the hue bridge
		"""

		bridge = None

		max_connect_tries = 3		
		for i in range(max_connect_tries):
			try:				
				#get the dridge	
				bridge = Bridge(config['DEFAULT']['HUE_BRIDGE_IP'],
								 config_file_path=config['DEFAULT']['HUE_CONFIG_FILE'])
				break
			except PhueRegistrationException:
				print("push the button on the hue bridge, waiting 15 sec for {}:th attempt out of {}".format(i+1, max_connect_tries))
				time.sleep(15)			

		return bridge

	@property
	def devices(self):
		lights = self.bridge.get_light_objects()
		mylights = []
		for i,light in enumerate(lights):
			mylights.append(PhilipsLamp(light, self.bridge_id+i+1))
		return mylights

	def command_subjects(self, vcommand, light_id=None):
		"""a middle man to before sending command to a light
			Receives vargs, which is a list of extra voice command arguments
		"""
		print("command lights called")
	
		action = vcommand.arguments[0]

		func = None

		for command in self.commands:
			if action == command.action:
				func = command.action_func
				break

		if not func:
			return False

		lights = self.bridge.get_light_objects()
		lights_reachable = 0

		for light in lights:
			if light.reachable:
				#if light id is given
				if light_id and not(light_id == ligt.light_id):
					continue

				lights_reachable += 1
				func(light, vargs=vcommand.arguments[1:])

		return lights_reachable > 0	
			


	def toggle_on(self, light, vargs=[]):

		light.brightness = 254
		


	def toggle_off(self, light, vargs=[]):

		light.brightness = 0



	def dim_lights(self, light, vargs=[]):	

		print("dimming lights with args: ", vargs)	

		percent = 0.1
		coeff = 1
		if len(vargs) > 0:
			try:
				coeff = int(vargs[0])
			except:
				pass
		percent = coeff * percent

		cur_brightness = light.brightness
		print("vanha kirkkaus: ", cur_brightness)
		light.brightness = max(0, int(light.brightness - percent*254))
		print("uusi kirkkaus: ", light.brightness)


	def brighten_lights(self, light, vargs=[]):	

		print("brightening lights with args: ", vargs)	

		percent = 0.1
		coeff = 1
		if len(vargs) > 0:
			try:
				coeff = int(vargs[0])
			except:
				pass
		percent = coeff * percent	

		cur_brightness = light.brightness
		print("vanha kirkkaus: ", cur_brightness)
		light.brightness = min(254, int(light.brightness +  254 * percent))
		print("uusi kirkkaus: ", light.brightness)


	def __repr__(self):
		return "PhilipslampInterface"
		


class SamsungTvInterface(DeviceInterface):	

	def __init__(self, config):
		"""The class initialized should match the one in the 
			config
		"""		
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))
		
		#immediately create an instance of the correct class
		new_device = SamsungTV( nice_name = config['DEFAULT']['NICE_NAME'],
								full_name = config['DEFAULT']['FULL_NAME'],
								location = config['DEFAULT']['LOCATION'],
								dev_id = config['DEFAULT']['DEVICE_ID'],
								is_on = False,
								enabled = True)

		self._devices = [new_device]


		self.target = "tv"

		#2d array of [["valot", "päälle", func ] ]
		self.commands = [ DeviceCommand(self.target, "päälle", self.toggle_on),
						DeviceCommand(self.target, "pois", self.toggle_off)	 ]	

	def command_subjects(self,vcommand):

		action = vcommand.arguments[0]

		for command in self.commands:
			if action == command.action:
				print("performing ", vcommand.target, " ", action , 
					"\nfor device ", self)

				command.action_func( vargs=vcommand.arguments[1:])
		


	def toggle_on(self):
		"""
			a dummy implementation
		"""
		logging.debug("{} toggled on".format(self.nice_name))

		self.is_on = not self.is_on

		return True

	def toggle_off(self):
		"""
			a dummy implementation
		"""
		logging.debug("{} toggled off".format(self.nice_name))

		self.is_on = not self.is_on

		return True




class Device(object):
	"""
	The parent class for all the devices
	"""
	def __init__(self, nice_name, full_name, location, dev_id, is_on, enabled):

		logging.debug("initialiasing {}".format(full_name) )

		self.nice_name = nice_name
		self.full_name = full_name
		self.location = location
		self.id = dev_id

		self.is_on = is_on
		self.enabled = enabled



class PhilipsLamp(Light):

	def __init__(self, light, light_id):

		mname = light.name
		self.nice_name = mname
		self.full_name = mname
		self.location = mname
		self.id = light_id

		self.is_on = light.on
		self.enabled = light.reachable


	def __repr__(self):
		return "Philipslamp object enabled: {}, on: {}".format( self.enabled, self.is_on)










class SamsungTV(Device, DeviceInterface):

	def __repr__(self):
		return "SamsungTV object enabled: {}, on: {}".format( self.enabled, self.is_on)