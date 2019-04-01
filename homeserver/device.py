

import logging

from phue import Light
#from homeserver.interface import DeviceInterface













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
		self.bridge_light_id = light.light_id #the id given by hue bridge

		self.is_on = light.on
		self.enabled = light.reachable


	def __repr__(self):
		return "Philipslamp object enabled: {}, on: {}".format( self.enabled, self.is_on)





#class SamsungTV(Device, DeviceInterface):
class SamsungTV(Device):

	def __repr__(self):
		return "SamsungTV object enabled: {}, on: {}".format( self.enabled, self.is_on)