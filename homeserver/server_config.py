

import configparser
import importlib
import sys
import os
from datetime import datetime


import logging



def load_config(file_path):
    """
    reads the config file and sets the found parameters to the app config
    """
    print("loading application configuration from path: {}".format(file_path))

    # default config does not exist 
    if not os.path.isfile(file_path):
        print("No server configuration file found at {}".format(file_path))
        print("Copy the homeserver/server_example.ini -> /homeserver/server.ini and update the fields")    
        return {}
    
    config = configparser.ConfigParser()
    try:
        config.read(file_path)

    except:
        print("reading configuration file {} failed.".format(file_path))
        return {}
        

    return config['DEFAULT']

	

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
    print("logging to file: ", log_file)
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

    rootLogger.info('Started logging')

    # return root logger (this is a bit unnecessary though)
    return rootLogger







	
	


