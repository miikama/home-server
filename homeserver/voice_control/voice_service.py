
import argparse
import os
import pyaudio
import wave
import multiprocessing
import time

from homeserver import config
from homeserver.voice_control import logger
from homeserver.voice_control.snowboy.snowboydecoder import HotwordDetector
from homeserver.voice_control.model_service import available_models


class VoiceService:

    # function name -> function
    _callbacks = {}    

    # keep track of the initialzed service
    # there should only be one of these 
    _running_instance = None

    name = "voiceservice"

    def __init__(self):

        logger.info("Initializing {}".format(self.name))
        if not VoiceService._running_instance is None:
            raise RuntimeError("Only single {} instance at a time supported".format(self.__class__.__name__))

        # set this instance to the current running
        VoiceService._running_instance = self

        # output event queue
        self._event_queue = None

    @staticmethod
    def get_running():
        return VoiceService._running_instance

    @staticmethod
    def get_current_queue():
        if VoiceService.get_running() is None:
            return None

        return VoiceService.get_running()._event_queue

    @staticmethod
    def add_callback(input_name, input_function):
        VoiceService._callbacks[input_name] = input_function

    @staticmethod
    def register_callback(func):
        """
            this can be added to functions that can act as voice triggered
        """         
        
        VoiceService.add_callback(func.__name__, func)                    

        return func

    @staticmethod
    def available_callbacks():
        return [ VoiceService._callbacks[key] for key in VoiceService._callbacks]

    @staticmethod
    def get_updated_voice_configuration(config):
        """ 
            returns a dictionary of model_name -> callback
        """
        models, callbacks = VoiceService.get_current_callback_mapping(config)

        new_config = {}
        for model, callback in zip(models, callbacks):
            new_config[model.lower()] = callback.__name__.lower() if callback is not None else None
            
        return new_config

    @staticmethod
    def get_current_callback_mapping(config):
        """
            Returns tuple of currently available models -> callback-function name

            Parses the callbacks in the from the configuration and maps them 
            to the functions registered as callbacks
        """
        model_to_callback = config.get('VOICE')

        if not model_to_callback:
            model_to_callback = {}

        all_models = available_models()
        corresponding_callbacks = []

        # all possible callbacks
        all_callbacks = VoiceService.available_callbacks()   

        # if model is not listed in the configuration yet, add it        
        for model in all_models:            
            if not model.lower() in model_to_callback:
                corresponding_callbacks.append(None)
                logger.warn("model {} not found in config".format(model.lower()))
                continue
            
            # this model has a configurated callback
            # check that this callback is an actual function
            callback_found = False
            for callback in all_callbacks:
                # just comparing callback names as lower case
                if callback.__name__.lower() == model_to_callback[model.lower()].lower():
                    corresponding_callbacks.append(callback)
                    callback_found = True
                    break
            
            # if no callback was found, add None
            if not callback_found:
                logger.warn("No callback function for callback '{}' found".format(
                                            model_to_callback[model.lower()].lower()))
                corresponding_callbacks.append(None)

        return all_models, corresponding_callbacks

    def start_service(self, event_queue: multiprocessing.Queue):
        logger.info("Starting voice service")

        self._event_queue = event_queue

        models = available_models(path_type='absolute')

        # mapping from models to callbacks 
        _, callbacks = VoiceService.get_current_callback_mapping(config)

        detector = HotwordDetector(models, sensitivity=[.6,.6,.6])
        detector.start(callbacks)

        raise RuntimeError("Should not get here.")

        #start_time = time.time()
        #while True:
            #self._event_queue.put("Voice service has run {} s.".format(time.time() - start_time))
            #time.sleep(1)









def print_model_to_callback():
    model_name, callback_func = VoiceService.get_current_callback_mapping(config)

    print("""
Currently the models are mapped to following callbacks:
    """)
    for name, func in zip(model_name, callback_func):        
        print("%25s  ---->  %20s" % (name, func.__name__ if func is not None else ""))
    
    print("")

def print_available_callbacks():
    callbacks = VoiceService.available_callbacks()

    print("""
Currently available callback functions:
    """)
    for callback in callbacks:
        print(callback.__name__)

    print("")




def create_detector(model_path):
    return HotwordDetector(model_path, sensitivity=0.5)

def run_detection():
    models = available_models(path_type='absolute')

    _,callbacks = VoiceService.get_current_callback_mapping(config)

    print("Detection starting")

    detector = HotwordDetector(models, sensitivity=[.6,.6,.6])
    detector.start(callbacks)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--model-path', required=True,
                        help="The path of the snowboy model")

    args = parser.parse_args()
    detector = create_detector(args.model_path)

    
    detector.start(detected_callback= lambda: print("detection callback lambda."))