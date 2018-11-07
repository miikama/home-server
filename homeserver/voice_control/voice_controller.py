

from homeserver.voice_control.google_speech import GoogleVoiceRecognition
from homeserver.voice_control.detect_voice_key import KeyWordDetector

from homeserver import app

import logging
import datetime


class VoiceController():

	def __init__(self, start=True):

		self.google_recognizer = GoogleVoiceRecognition(app.config['GOOGLE_CREDENTIALS'])

		if start:
			self.start()



	def start(self):

		#start the keyword detection
		key_detector = KeyWordDetector(app.config['SNOWBOY_MODEL'],
								detected_callback= self.detection_callback ,
								audio_recorder_callback=self.google_recognizer.interpret_command,
				              	silent_count_threshold=15,
				              	recording_timeout=10,
				              	audio_path=app.config['AUDIO_PATH_AFTER_DETECTION'])


	def detection_callback(self):

		"""This is called when the hot word is detected, this just logs the time
			keyword is detected. The actual handling is done after audio is recorder 
			in audio detection callback
		"""
		
		logging.debug("Keyword detected at {}".format(datetime.datetime.now().isoformat() ) ) 


