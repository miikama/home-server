

#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import io
import os

# Imports the Google Cloud client library
# [START speech_python_migration_imports]
from google.cloud import speech
from google.cloud.speech import enums, types

# class for recording 
from homeserver.voice_control.voice_service import record_audio


class GoogleVoiceRecognition():

	def __init__(self, google_api_credential_path):

		print("initialising google voice recognition")
	
		"""
		Give an absolute path to the google credentials (loaded from server.ini)
		"""
	
		#instead create the client from a credential json
		self.client =speech.SpeechClient.from_service_account_file(google_api_credential_path)
		

	

	def listen_to_command(self):

		command_time = 4

		print("Starting recording for google")

		if not self.client:
			print("no client for google")
			return None
		

		#listen to microphone

		file_name = record_audio(command_time, os.path.join(os.path.dirname(__file__), 'resources', 'mysound.vaw'))

		if not file_name:
			print("failure in recording")
			return None

		self.interpret_command(file_name)
		

	def interpret_command(self, file_name, keyphrases=[]):
		"""
			Sends given audio file (with full path) to google and returns 
			the interpreted speech as string.
			Keyphrases is an optional list of strings that helps google notice
			keywords
		"""

		print("sending audio to google")
		
		# Loads the audio into memory
		with io.open(file_name, 'rb') as audio_file:
		    content = audio_file.read()
		    audio = types.RecognitionAudio(content=content)

		#loads the keyphrases into an object
		speech_context = speech.types.SpeechContext(phrases=keyphrases)

		config = types.RecognitionConfig(
		    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
		    sample_rate_hertz=16000,
		    language_code='fi-FI',		    #en-US
			speech_contexts=[speech_context])
			

		# Detects speech in the audio file
		response = self.client.recognize(config, audio)

		transcript = None
		#only take the first result and the first transcript
		for result in response.results:
		    print('Transcript: {}'.format(result.alternatives[0].transcript))
		    transcript = result.alternatives[0].transcript
		    break


		return transcript






