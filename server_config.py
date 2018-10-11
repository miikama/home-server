
import cPickle as pickle

from datetime import datetime


LOADED_CONFIG = None



class Config():
	'''
	A class of containing the application configurations
	'''

    def __init__(self, **kv):

    	if not LOADED_CONFIG:

			self.created = datetime.now()
			self.version = 0.1

	

def load_config():


