

class Device(object):
	"""
	The parent class for all the devices
	"""
	def __init__(self, config):

		print("initialiasing ", config['DEFAULT']['FULL_NAME'])

		self.nice_name = config['DEFAULT']['NICE_NAME']
		self.full_name = config['DEFAULT']['FULL_NAME']
		self.location = config['DEFAULT']['LOCATION']




class PhilipsLamp(Device):

	def __init__(self, config):

		# calling the parent class constructor first
		super(PhilipsLamp,self).__init__(config)



