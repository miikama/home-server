from homeserver import app


class Device(object):
	"""
	The parent class for all the devices
	"""
	def __init__(self, config):

		app.logger.debug("initialiasing ", config['DEFAULT']['FULL_NAME'])

		self.nice_name = config['DEFAULT']['NICE_NAME']
		self.full_name = config['DEFAULT']['FULL_NAME']
		self.location = config['DEFAULT']['LOCATION']
		self.id = config['DEFAULT']['DEVICE_ID']

		self.is_on = False
		self.enabled = True


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

		print(self.nice_name, " toggled on/off")



		self.is_on = not self.is_on

		return True


class PhilipsLamp(Device):

	def __init__(self, config):

		# calling the parent class constructor first
		super(PhilipsLamp,self).__init__(config)



