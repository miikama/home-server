
from homeserver.voice_control.voice_service import VoiceService 

@VoiceService.register_callback
def detection_callback():
    print("Detected stuff")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put("Detected stuff")

@VoiceService.register_callback
def lights_on():
    print("lights on")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put("lights on")

@VoiceService.register_callback
def lights_off():
    print("lights off")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put("lights off")

@VoiceService.register_callback
def dim_lights():
    print("dim lights")

    queue = VoiceService.get_current_queue()
    if queue:
        queue.put("dim lights")