

from homeserver.voice_control.google_speech import GoogleVoiceRecognition
from homeserver.voice_control.snowboy.snowboydecoder import HotwordDetector, play_audio_file

#make the voicecontrol follow the device interface structure for control
from homeserver.interface import DeviceInterface, DeviceTarget

# import the DeviceCommand
from homeserver.command_handler import DeviceCommand

from homeserver import app, logger, device_handler


import datetime
import threading 





class VoiceThread(threading.Thread):

	def __init__(self, parent=None, **kvargs):
		self.parent = parent
		super(VoiceThread, self).__init__(**kvargs)




class VoiceController(DeviceInterface):

	def __init__(self, start=True):

		#### variables for the DeviceInterface ###
		self.name="Voice Control"
		self.connected = False
		self.is_on = False
		self.running = False
		self._devices = []
		self.targets = set('voice_control')
		self.commands = [DeviceTarget(self.targets, "toggle", self.toggle_detection)]
		self.dev_id = 200000 #TODO: read this from some config or smth
		### #############  ###


		self.google_recognizer = GoogleVoiceRecognition(app.config['GOOGLE_CREDENTIALS'])
		#a list of strings to help google speect to text
		self.google_keyphrases = device_handler.get_voice_keys()

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
		self.vthread = VoiceThread(target=self._start_detection, parent=self)		


	def start_detector(self):
		"""
			Method to be called outside the VoiceController class to start 
			the detection.
		"""

		self.initialize_detector()

		self.vthread.start()

		self.is_on = True
		self.connected = True		
		self.running = True

		logger.info('Keyword detector started')

	def _start_detection(self):

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
		
		logger.debug("Keyword detected at {}".format(datetime.datetime.now().isoformat() ) ) 

	def audio_recorded_callback(self, fname):
		"""
			Called when after detecting keyword an audioclip has done recorded and saved
			recognizes what was said and then acts on the interpreted audio
		"""

		command_string = self.google_recognizer.interpret_command(fname, 
													keyphrases=self.google_keyphrases)	

		logger.debug("command_string: {}".format(command_string))

		if command_string:	

			command = DeviceCommand.command_from_string(command_string)

			logger.debug("sending command to device_handler: {}".format(command))

			device_handler.handle_voice_command(command)




	def toggle_detection(self):

		if self.running:
			self.stop_detection()
		else:
			self.start_detector()


	def stop_detection(self):
		logger.info("Stopping voice detection")
		self.interrupted = True
		self.vthread.join()
		self.running = False
		self.is_on = False		
		logger.info("Voice detection halted")


	def interrupt_callback(self):
		return self.interrupted


	def command_subjects(self,command, *args):
		"""Base methods, common error checking for all base classes implemented here"""

		super().command_subjects(command)

		#parse command	
		if len(command.arguments) < 1:
			return


		action = command.arguments[0]		
		func = None

		# match the action in the command to the commands of this class
		for command in self.commands:
			if action == command.action:
				func = command.action_func
				break

		if func is not None:
			func()

