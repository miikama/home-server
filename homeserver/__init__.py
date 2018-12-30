
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

#start voice control
from homeserver.voice_control.voice_controller import VoiceController
voice_controller = VoiceController(start=True)
device_handler.add_interface(voice_controller)



