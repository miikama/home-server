
import sys
import os
import logging

from flask import Flask


HOME_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))


#the absolute path of this script
app_path =  os.path.dirname(os.path.realpath(__file__))

#config for the project
from homeserver.server_config import load_config, setup_logging
config = load_config(os.path.join(app_path, 'server.ini'))

# update logger settings
logger =setup_logging(config, logging.DEBUG)

#load devices and connect them
from homeserver.device_handler import DeviceHandler
device_handler = DeviceHandler( os.path.join( app_path, 'device_configs') )

def create_app(config):


	#init the app
	app = Flask(__name__)

	#add the config parameters to the app config
	app.config.update(config)

	#load the webpage routes
	from homeserver.server import api_routes
	app.register_blueprint(api_routes)


	#start voice control
#	from homeserver.voice_control.voice_controller import VoiceController
#	app.voice_controller = VoiceController(start=True)
#	app.device_handler.add_interface(app.voice_controller)



	return app




app = create_app(config)




