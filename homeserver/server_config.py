

import configparser
import importlib
from datetime import datetime

from homeserver import app

import logging



def load_config(file_path):
	"""
	reads the config file and sets the found parameters to the app config
	"""
	logging.debug("loading application configuration from {}".format(file_path))
	config = configparser.ConfigParser()
	try:
		config.read(file_path)
	except Exception as e:
		return None

	for key in config['DEFAULT'].keys():
		app.config[key.upper()] = config['DEFAULT'][key]



	

def read_device_config(file_path):
	"""Loads a config file and uses the DEVICE_CLASS parameter of 
	the config file to instantiate a right device class
	"""
	logging.debug("loading devices from {}".format(file_path))
	config = configparser.ConfigParser()
	try:
		config.read(file_path)
	except Exception as e:
		return None
	

	logging.debug("loaded device config {}".format(config))

	#import the device classes with importlib
	DeviceClass = getattr(importlib.import_module("homeserver.device"), config['DEFAULT']['DEVICE_CLASS'])

	#immediately create an instance of the correct class
	new_device = DeviceClass(config)


	return new_device	


	
	


