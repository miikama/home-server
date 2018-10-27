
import os
import logging

from flask import Flask



#the absolute path of this script
app_path =  os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)


#load different api keys and configurations
from homeserver.server_config import load_config
load_config(os.path.join(app_path, 'server.ini'))
logging.basicConfig(filename=os.path.join(app_path,app.config['LOG_FILE']),level=logging.INFO)


#load devices
from homeserver.device_handler import DeviceHandler
device_handler = DeviceHandler( os.path.join( app_path, 'device_configs') )

#get the webpage rolling
from homeserver import server  
