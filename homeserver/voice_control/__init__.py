
import os
import logging

VOICE_CONTROL_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger("VoiceControl")

from homeserver import config

# import voice callbacks
from .voice_callbacks import *

# Once we import anythin from voice-control the configuration parameters are added to 
# the homeserver configuration
from .voice_service import VoiceService
config.add_configuration_parameters("VOICE", VoiceService.get_updated_voice_configuration(config))