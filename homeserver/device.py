import logging
import configparser
import importlib

from homeserver import app


from phue import Bridge
import random


class DeviceInterface():
	"""
	A class that hides the fact that multiple devices are controlled by 
	a single control point
	"""

	_devices = []

	def __init__(self, config):

		""" Loads a config file and uses the DEVICE_CLASS parameter of 
		the config file to instantiate a right device class

		The class initialized should match the one in the config		
		"""

		raise NotImplementedError("Abstract base class")


	@property
	def devices(self):
		return self._devices


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





class PhilipsLampInterface(DeviceInterface):
	
	def __init__(self, config):

		"""The class initialized should match the one in the 
			config
		"""
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not this class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))
		
		#immediately create an instance of the correct class
		new_device = PhilipsLamp(self, config)

		self._devices = [new_device]


		


class SamsungTvInterface(DeviceInterface):	

	def __init__(self, config):
		"""The class initialized should match the one in the 
			config
		"""		
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))
		
		#immediately create an instance of the correct class
		new_device = SamsungTV(config)

		self._devices = [new_device]




class Device(object):
	"""
	The parent class for all the devices
	"""
	def __init__(self, config):

		logging.debug("initialiasing {}".format(config['DEFAULT']['FULL_NAME']) )

		self.nice_name = config['DEFAULT']['NICE_NAME']
		self.full_name = config['DEFAULT']['FULL_NAME']
		self.location = config['DEFAULT']['LOCATION']
		self.id = config['DEFAULT']['DEVICE_ID']

		self.is_on = False
		self.enabled = True

		#2d array of [["valot", "päälle", func ] ]
		self.commands = []

		#used to give this device commands
		self.target = None



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
		

	def toggleOn(self):
		"""
			a dummy implementation
		"""
		logging.debug("{} toggled on".format(self.nice_name))

		self.is_on = not self.is_on

		return True

	def toggleOff(self):
		"""
			a dummy implementation
		"""
		logging.debug("{} toggled off".format(self.nice_name))

		self.is_on = not self.is_on

		return True







class PhilipsLamp(Device):

	def __init__(self, interface, config):

		# calling the parent class constructor first
		super().__init__(config)

		self.target = "valot"

		#2d array of [["valot", "päälle", func ] ]
		self.commands = [ {'action':"päälle", 'action_func':self.toggleOn},
						{'action':"pois", 'action_func':self.toggleOff}	 ]

	def toggleOn(self):



		b = Bridge(app.config['HUE_BRIDGE_IP'])

		# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
		#b.connect()

		# Get the bridge state (This returns the full dictionary that you can explore)
		b.get_api()

		from pprint import pprint

		lights = b.get_light_objects()

		pprint(lights)

		for light in lights:
			light.brightness = 254
		light.xy = [random.random(),random.random()]

		return super(PhilipsLamp,self).toggleOn()




	def toggleOff(self):

		b = Bridge(app.config['HUE_BRIDGE_IP'])

		# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
		#b.connect()

		# Get the bridge state (This returns the full dictionary that you can explore)
		b.get_api()

		from pprint import pprint

		lights = b.get_light_objects()

		pprint(lights)

		for light in lights:
			light.brightness = 0
		light.xy = [random.random(),random.random()]


		return super(PhilipsLamp,self).toggleOff()



	def __repr__(self):
		return "Philipslamp object enabled: {}, on: {}".format( self.enabled, self.is_on)










class SamsungTV(Device, DeviceInterface):

	def __init__(self, config):

		# calling the parent class constructor first
		super(SamsungTV,self).__init__(config)

		self.target = "tv"

		#2d array of [["valot", "päälle", func ] ]
		self.commands = [ {'action':"päälle", 'action_func':self.toggleOn},
						{'action':"pois", 'action_func':self.toggleOff}	 ]	

	def __repr__(self):
		return "SamsungTV object enabled: {}, on: {}".format( self.enabled, self.is_on)