import logging
import configparser
import importlib
import time, os
import threading

from homeserver import app


from phue import Bridge, Light, PhueRegistrationException, PhueRequestTimeout
import random






###################### classes used internally by the interfaces #######################






class DeviceCommand():
	"""wrapper class for internal use for the devices"""

	def __init__(self,targets, action, action_func):
		"""has target device, arguments,and a function to be called """
		self.targets = targets
		self.action = action
		self.action_func = action_func


class StateUpdateThread(threading.Thread):

	def __init__(self, interface=None, wait_time=30, **kvargs):
		self.pause_updates = threading.Event()
		self.stop_thread = threading.Event()
		self.interface =interface
		self.wait_time = wait_time
		super().__init__(**kvargs)

	def run(self):

		while not self.stop_thread.is_set():
			if not self.pause_updates.is_set():
				logging.info("updating {}".format(self.interface))				
				self.interface.update_devices()
			time.sleep(self.wait_time)










############### A base class for all interfaces #########################








class DeviceInterface():
	"""
	A class that hides the fact that multiple devices are controlled by 
	a single control point
	"""

	

	def __init__(self, dev_id, config=None):

		""" Loads a config file and uses the DEVICE_CLASS parameter of 
		the config file to instantiate a right device class

		The class initialized should match the one in the config		
		"""

		self.name = "default interface name"

		self.dev_id = dev_id

		self.connected = False	

		self.is_on = False

		self._devices = []	# list of [Device]
		
		self.commands = [] # List of [DeviceCommand(), ...]
		
		self.targets = set() #set of strings this device can be commanded with



	@property
	def devices(self):
		return self._devices

	def update_devices(self):
		""" function called from a thread which handles the state updates """
		print("update_devices of the base class called")


	def command_subjects(self,vcommand):
		"""Base methods, common error checking for all base classes implemented here"""

		if vcommand.target not in self.targets:
			raise ValueError("The voicecommand target should be found in the Devicecommand targets")
		
		#return NotImplementedError("Abstract base class")




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
		if self.targets is not None:
			for target in self.targets:
				keywords.append(target)
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

	def __repr__(self):
		return "{} {}".format(type(self).__name__, self.name)

	def __str__(self):
		return "{} {}".format(type(self).__name__, self.name)










###################### Interface for the philips lamp ######################












class PhilipsLampInterface(DeviceInterface):
	
	def __init__(self, config):

		"""The class initialized should match the one in the 
			config
		"""
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not this class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))

		self.name = "Philips Lamp Bridge"
		self.connected = False
		self.is_on = False

		self.config = config

		self.targets = set(["valot", "philips_light"])

		self.commands = [ DeviceCommand(self.targets, "päälle", self.toggle_on),
							DeviceCommand(self.targets, "pois", self.toggle_off),
							DeviceCommand(self.targets, "alas", self.dim_lights),
							DeviceCommand(self.targets, "ylös", self.brighten_lights)]


		self.dev_id = int(config['DEFAULT']['DEVICE_ID'])

		#dont connect to the bridge in the initialization because can timeout, 
		#this will be done first time there is a call to the lights
		#self.bridge = self.connect_to_hue_bridge(config)
		self.bridge = None

		#an offline list of all the devices 
		self._devices = []


		self.update_thread = StateUpdateThread(interface=self, wait_time=30)
		self.update_thread.start()


	def connect_to_hue_bridge(self, config):
		"""	function to establish a connection to the hue bridge """

		bridge = None
			
		if not self.bridge_available:
			return None

		max_connect_tries = 3		
		for i in range(max_connect_tries):
			try:				
				#get the dridge	
				bridge = Bridge(config['DEFAULT']['HUE_BRIDGE_IP'],
								 config_file_path=config['DEFAULT']['HUE_CONFIG_FILE'])
				self.connected = True				
				break
			except PhueRegistrationException:
				print("push the button on the hue bridge, waiting 15 sec for {	}:th attempt out of {}".format(i+1, max_connect_tries))
				time.sleep(15)	
			except PhueRequestTimeout:
				#actually cannot timeout because initialising bridge does not check whether hue bridge is available
				print("cannot connect to bridge")
				break

		return bridge

	@property
	def bridge_available(self):
		"""tries to make an api request to the bridge to see whether it is there in the expected ip"""
		return False



	def update_devices(self):
		"""	
			This method actually connects to hue bridge,
			can timeout with PhueTimeoutException
		"""
		#connect to the bridge if not connected already, can timeout
		if not self.bridge:
			self.bridge = self.connect_to_hue_bridge(self.config)
		#no connections established
		if not self.bridge:
			logging.info("NO CONNECTION TO HUE BRIDGE")
			self.connected = False
			self.is_on = False
			return []



		lights = self.bridge.get_light_objects()
		mylights = []
		for i,light in enumerate(lights):
			mylights.append(PhilipsLamp(light, self.dev_id+i+1))
		return mylights



	def command_subjects(self, vcommand, light_id=None):
		"""a middle man to before sending command to a light
			Receives vargs, which is a list of extra voice command arguments
		"""
		super().command_subjects(vcommand) #error handling

		#if we are not connected we cannot command device
		if not self.connected:
			return False
		
		#parse command	
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
				if light_id and not (light_id == ligt.light_id):
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












##################### Interface for the samsung TV (dummy implementation) ######################
	






class SamsungTvInterface(DeviceInterface):	

	def __init__(self, config):
		"""The class initialized should match the one in the 
			config
		"""		
		if not config['DEFAULT']['DEVICE_CLASS'] == type(self).__name__:
			raise NameError("trying to initialize {}, which is not class {}".format(config['DEFAULT']['DEVICE_CLASS'], cls.__name__))


		self.name = "Samsung TV"
		self.connected = False
		self.is_on = False
		self.dev_id = int(config['DEFAULT']['DEVICE_ID'])

		#immediately create an instance of the correct class
		new_device = SamsungTV( nice_name = config['DEFAULT']['NICE_NAME'],
								full_name = config['DEFAULT']['FULL_NAME'],
								location = config['DEFAULT']['LOCATION'],
								dev_id = config['DEFAULT']['DEVICE_ID'],
								is_on = False,
								enabled = True)

		self._devices = [new_device]




		self.targets = set(["tv", "samsung_tv"])

		#2d array of [["valot", "päälle", func ] ]
		self.commands = [ DeviceCommand(self.targets, "päälle", self.toggle_on),
						DeviceCommand(self.targets, "pois", self.toggle_off)	 ]	

	def command_subjects(self,vcommand):
		# error handling
		super().command_subjects(vcommand) 

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










################## separate Device classes #######################









class Device(object):
	"""
	The parent class for all the devices
	"""
	def __init__(self, nice_name, full_name, location, dev_id, is_on, enabled):

		logging.debug("initialiasing {}".format(full_name) )

		self.nice_name = nice_name
		self.full_name = full_name
		self.location = location
		self.dev_id = dev_id

		self.is_on = is_on
		self.enabled = enabled



class PhilipsLamp(Light):

	def __init__(self, light, light_id):

		mname = light.name
		self.nice_name = mname
		self.full_name = mname
		self.location = mname
		self.dev_id = light_id

		self.is_on = light.on
		self.enabled = light.reachable


	def __repr__(self):
		return "Philipslamp object enabled: {}, on: {}".format( self.enabled, self.is_on)





class SamsungTV(Device, DeviceInterface):

	def __repr__(self):
		return "SamsungTV object enabled: {}, on: {}".format( self.enabled, self.is_on)