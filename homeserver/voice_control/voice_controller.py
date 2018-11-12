

from homeserver.voice_control.google_speech import GoogleVoiceRecognition
from homeserver.voice_control.snowboydecoder import HotwordDetector, play_audio_file

from homeserver import app, device_handler

import logging
import datetime
import threading 



class VoiceCommand():

	"""a class encapsulating the voice commands
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



	def __repr__(self):
		return "VoiceCommand on target {} with arguments: {}".format(self.target, *self.arguments)





class VoiceThread(threading.Thread):

	def __init__(self, parent=None, **kvargs):
		self.parent = parent
		super(VoiceThread, self).__init__(**kvargs)
	
	def terminate(self):

		#after the loop finishes, clean up the audio reservation
		self.parent.detector.terminate()








class VoiceController():

	def __init__(self, start=True):

		self.google_recognizer = GoogleVoiceRecognition(app.config['GOOGLE_CREDENTIALS'])

		self.interrupted = False

		#some parameters, seem okay for two word command
		self.silent_count_threshold = 7	
		self.recording_timeout = 5


		self.detector = HotwordDetector(app.config['SNOWBOY_MODEL'], sensitivity=0.5)
		print('Listening for voice keyword...')

		#set the path of the audio file saved
		self.detector.set_recording_filepath(app.config['AUDIO_PATH_AFTER_DETECTION'])

		#the voicethread
		self.vthread = VoiceThread(target=self.start_detector, parent=self)

		self.voice_callbacks = {}


		if start:
			self.start()



	def start(self):
		"""	starts the voicecontrol thread	"""		

		self.vthread.start()


	def start_detector(self):
		
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

		command_string = self.google_recognizer.interpret_command(fname)	

		print("command_string: ", command_string)

		if command_string:	

			command = VoiceCommand.command_from_string(command_string)

			print("sending command to device_handler: ", command )

			device_handler.handle_voice_command(command)






	def stop_detection(self):
		print("stopping detection")
		self.interrupted = True
		self.p.terminate()


	def interrupt_callback(self):
		return self.interrupted

