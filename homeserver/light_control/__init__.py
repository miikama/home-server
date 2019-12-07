import os
import logging

LIGHT_CONTROL_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger("LightControl")


from homeserver import config

# Once we import anythin from voice-control the configuration parameters are added to 
# the homeserver configuration
from .lights_service import LightsService
config.add_configuration_parameters("LIGHTS", LightsService.update_light_configuration(config))