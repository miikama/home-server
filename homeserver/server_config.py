

import configparser
import importlib
import sys
import os
from datetime import datetime


from homeserver import HOME_SERVER_DIR

import logging

"""
    During the first run of the homeserver a configuration file is generated.
    
    Some fields are left as 'empty' and are initialized during the first run
    of different subprograms.
"""

class Config:
    
    SNOWBOY_API_KEY=""
    FLASK_SECRET_KEY=""

def get_config_file_path():
    return os.path.join(HOME_SERVER_DIR, "server.ini")      

def write_config(config: Config, config_out_path: str):

    # log is stored under homeserver     
    init_file = config_out_path
    
    parser = get_config_parser(config)
    
    with open(init_file, 'w') as outfile:
        parser.write(outfile)

def get_config_parser(config: Config):

    parser = configparser.ConfigParser()

    parser['DEFAULT'] = {
        'SNOWBOY_API_KEY': config.SNOWBOY_API_KEY,
        'FLASK_SECRET_KEY': config.FLASK_SECRET_KEY,
    }

    return parser


def load_config(file_path=""):
    """
    reads the config file and sets the found parameters to the app config
    """
    if not file_path:
        file_path = get_config_file_path()
    
    # default config does not exist 
    if not os.path.isfile(file_path):
        # write default config        
        write_config(Config(), file_path)        
        
    parser = configparser.ConfigParser()
    try:
        parser.read(file_path)
    except:
        print("reading configuration file {} failed.".format(file_path))
        return {}        

    return parser['DEFAULT']
	

def read_device_config(file_path):
    """Loads a config file and uses the DEVICE_CLASS parameter of 
    the config file to instantiate a right device class
    """
    logging.debug("loading devices from {}".format(file_path))
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
    except Exception as e:
        return None


    logging.debug("loaded device config {}".format(config))

    #import the device classes with importlib
    DeviceClass = getattr(importlib.import_module("homeserver.device"), config['DEFAULT']['DEVICE_CLASS'])

    #immediately create an instance of the correct class
    new_device = DeviceClass(config)


    return new_device	




############### logging ######################

class MyFilter(object):
    """
    	Create a logging filter that shows log 
    	messages with smaller criticality than
    	the given level
    """
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):        
        return logRecord.levelno <= self.__level


def update_config():

    pass


def setup_logging(config, log_level):
    """
        Given the initial server log file path,
        set up the server root logger.

        Send all log messages to log_file, and info
        messages to console
    """

    log_file = config.get('LOG_FILE') 
    if not log_file: 
        log_file = "server.log"    
    # get the python logging root logger
    rootLogger = logging.getLogger()

    # log only debug and higher to the logfile
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    

    # log everything but debug to console	
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.addFilter(MyFilter(logging.INFO))
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(levelname)-8s] %(message)s')
    # tell the handler to use this format
    console_handler.setFormatter(formatter)

    rootLogger.addHandler(file_handler)
    rootLogger.addHandler(console_handler)
    rootLogger.setLevel(log_level)

    # return root logger (this is a bit unnecessary though)
    return rootLogger







	
	


