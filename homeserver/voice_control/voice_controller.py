

from homeserver.voice_control.google_speech import GoogleVoiceRecognition
from homeserver.voice_control.snowboydecoder import HotwordDetector, play_audio_file

#make the voicecontrol follow the device interface structure for control
from homeserver.interface import DeviceInterface, DeviceCommand


from homeserver import app, logger

import logging
import datetime
import threading 




class VoiceCommand():

	"""a class encapsulating the voice commands


		Possible interfaces:
			PhilipsLamp:
				targets:  "valot", "philips_light"

				commands: "päälle", "pois", "alas", "ylös"

			SamsungTV:
				targets: "tv", "samsung_tv"
		
				commands: "päälle", "pois"

	"""

	def __init__(self, target=None,arguments=[] ):
		"""
		@params: target: string, the device/thing affected
				arguments: list of strings of that determine 
				what should the device/thing in question do
		 """
		if target:	 		
			self.target	= target.lower()
		else:
			self.target = target

		self.arguments = arguments
		for i in range(len(self.arguments)):
			self.arguments[i] = self.arguments[i].lower()

	@classmethod
	def command_from_string(cls, command_string ):
		"""
		a class constructor to create a new voicecommand from a string

		if the command string only has one word, it is interpreted 
		as a command to the active device, and the target of the command 
		is left as None

		"""
		splitted = command_string.split(' ')

		if len(splitted) == 1:
			return cls( arguments=splitted )

		else:
			target = splitted[0]
			args = splitted[1:]
			return cls(target=target, arguments=args)


	@classmethod
	def command_from_api(cls, target, command_name):
		"""
			Class constructor from the interface

		"""
		logger.info("creating command from api with target {} and command {}".format(target, command_name))

		return cls(target=target, arguments=[command_name])




	def __repr__(self):
		return "VoiceCommand on target {} with arguments: {}".format(self.target, self.arguments)




class VoiceThread(threading.Thread):

	def __init__(self, parent=None, **kvargs):
		self.parent = parent
		super(VoiceThread, self).__init__(**kvargs)
	
	def terminate(self):

		#after the loop finishes, clean up the audio reservation
		self.parent.detector.terminate()









class VoiceController(DeviceInterface):

	def __init__(self, start=True):

		#### variables for the DeviceInterface ###
		self.name="Voice Control"
		self.connected = True
		self.is_on = True
		self.running = False
		self._devices = []
		self.targets = set('voice_control')
		self.commands = [DeviceCommand(self.targets, "toggle", self.toggle_detection)]
		self.dev_id = 200000 #TODO: read this from some config or smth
		### #############  ###


		self.google_recognizer = GoogleVoiceRecognition(app.config['GOOGLE_CREDENTIALS'])
		#a list of strings to help google speect to text
		self.google_keyphrases = app.device_handler.get_voice_keys()

		self.interrupted = False

		#some parameters, seem okay for two word command
		self.silent_count_threshold = 2
		self.recording_timeout = 10

		# param to the snowboy detector
		self.sensitivity = 0.5

		self.model = app.config['SNOWBOY_MODEL']

		self.recording_path = app.config['AUDIO_PATH_AFTER_DETECTION']

		# the keyword detector is initialized in the start detector
		self.detector = None

		self.vthread = None

		self.voice_callbacks = {}

		if start:
			self.start_detector()		

	def initialize_detector(self):

		logger.info("model path: {}".format(self.model))

		self.detector = HotwordDetector(self.model, sensitivity=self.sensitivity)		

		#set the path of the audio file saved
		self.detector.set_recording_filepath(self.recording_path)	

		#the voicethread
		self.vthread = VoiceThread(target=self.start_detection, parent=self)		


	def start_detector(self):

		self.initialize_detector()

		self.vthread.start()
		
		self.running = True

		logger.info('Keyword detector started')

	def start_detection(self):

		# main loop
		self.detector.start(detected_callback=self.detection_callback,
		               interrupt_check=self.interrupt_callback,
		               sleep_time=0.03,
		               audio_recorder_callback=self.audio_recorded_callback,
		              	silent_count_threshold=self.silent_count_threshold,
		              	recording_timeout=self.recording_timeout)



	def detection_callback(self):

		"""This is called when the hot word is detected, this just logs the time
			keyword is detected. The actual handling is done after audio is recorder 
			in audio detection callback
		"""
		
		logging.debug("Keyword detected at {}".format(datetime.datetime.now().isoformat() ) ) 

	def audio_recorded_callback(self, fname):
		"""Called when after detecting keyword an audioclip has done recorded and saved
			recognizes what was said and then acts on the interpreted audio
		"""

		command_string = self.google_recognizer.interpret_command(fname, 
													keyphrases=self.google_keyphrases)	

		logging.debug("command_string: ", command_string)

		if command_string:	

			command = VoiceCommand.command_from_string(command_string)

			logging.debug("sending command to device_handler: ", command )

			app.device_handler.handle_voice_command(command)


	def command_subjects(self,vcommand, *args):
		"""Base methods, common error checking for all base classes implemented here"""

		super().command_subjects(vcommand)
		
		#parse command	
		action = vcommand.arguments[0]		
		func = None

		for command in self.commands:
			if action == command.action:
				func = command.action_func
				break

		if func is not None:
			func()

	def toggle_detection(self):

		if self.running:
			self.stop_detection()
		else:
			self.start_detector()





	def stop_detection(self):
		print("stopping detection")
		self.interrupted = True
		self.vthread.terminate()


	def interrupt_callback(self):
		return self.interrupted


