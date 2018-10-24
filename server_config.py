

import configparser
import importlib


from datetime import datetime


LOADED_CONFIG = None



class Config():
	"""
	A class of containing the application configurations
	"""

	def __init__(self, **kv):

		if not LOADED_CONFIG:

			self.created = datetime.now()
			self.version = 0.1



def load_config():

	pass


def read_device_config(file_path):
	"""Loads a config file and uses the DEVICE_CLASS parameter of 
	the config file to instantiate a right device class
	"""

	config = configparser.ConfigParser()
	try:
		config.read(file_path)
	except Exception as e:
		return None
	

	print(config)

	#import the device classes with importlib
	DeviceClass = getattr(importlib.import_module("device"), config['DEFAULT']['DEVICE_CLASS'])

	#immediately create an instance of the correct class
	new_device = DeviceClass(config)


	return new_device	


	
	


