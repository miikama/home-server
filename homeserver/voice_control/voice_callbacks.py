
from homeserver.voice_control.voice_service import VoiceService 
from homeserver.voice_control import logger
from homeserver.event_service import EventMessage

@VoiceService.register_callback
def detection_callback():
    logger.debug("Detected stuff")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put(EventMessage("detected_stuff", VoiceService.name))

@VoiceService.register_callback
def lights_on():
    logger.debug("lights_on")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put(EventMessage("lights_on", VoiceService.name))        

@VoiceService.register_callback
def lights_off():
    logger.debug("lights off")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put(EventMessage("lights_off", VoiceService.name))        

@VoiceService.register_callback
def dim_lights():
    logger.debug("dim_lights")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put(EventMessage("dim_lights", VoiceService.name))
