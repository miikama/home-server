
import os
import logging

from flask import Flask



#the absolute path of this script
app_path =  os.path.dirname(os.path.realpath(__file__))
#config for the project
from homeserver.server_config import load_config
config = load_config(os.path.join(app_path, 'server.ini'))
#set the logging route
logging.basicConfig(filename=os.path.join(app_path,config['LOG_FILE']),level=logging.DEBUG)


#now init the app with logging set up
app = Flask(__name__)


#add the config parameters to the app config
for key in config.keys():
	app.config[key.upper()] = config[key]

#load devices and connect them
from homeserver.device_handler import DeviceHandler
device_handler = DeviceHandler( os.path.join( app_path, 'device_configs') )



#get the webpage rolling
from homeserver import server  



from homeserver.voice_control.google_speech import GoogleVoiceRecognition
google_recognizer = GoogleVoiceRecognition(app.config['GOOGLE_CREDENTIALS'])

def m_call():
	print("kuulen!!!!!!!!!!, file: ")

def m_call2(fname):
	print("kuulen!!!!!!!!!!, file: ", fname)



#start the keyword detection
from homeserver.voice_control.detect_voice_key import KeyWordDetector
key_detector = KeyWordDetector(app.config['SNOWBOY_MODEL'],
									detected_callback= m_call ,
									audio_recorder_callback=google_recognizer.interpret_command,
					              	silent_count_threshold=15,
					              	recording_timeout=10,
					              	audio_path=app.config['AUDIO_PATH_AFTER_DETECTION'])


