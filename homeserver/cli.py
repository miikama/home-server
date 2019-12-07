import sys
import argparse

from homeserver.voice_control.model_service import print_available_models, train_new_model
from homeserver.voice_control.voice_service import run_detection, print_model_to_callback, print_available_callbacks

from homeserver.device_server.server import list_devices, run_server

from homeserver.light_control.lights_service import LightsService




class HomeCli:

    '''
        A common entrypoint for multiple different command line tools
    '''

    cli_commands = ('voice', 'devices', 'lights')

    usage = '''

hserv <command-name> [arguments]

command-name can be:
    voice   [voice-args]            
    devices [device-args]  
    lights [light-args]          
'''

    def __init__(self):

        parser = argparse.ArgumentParser(
            description="A common entrypoint for multiple different command line tools",
            usage=self.usage)       

        parser.add_argument('command',
                            help="Command is any of the following: {}".format(self.cli_commands))

                                    
        args = parser.parse_args(sys.argv[1:2])
        
        if args.command not in self.cli_commands:
            parser.print_help()
            sys.exit(1)

        # if the argument is marked as a possible command,
        # A method with the same name is invoked
        getattr(self, args.command)()

    def devices(self):

        parser = argparse.ArgumentParser(
            description="The CLI for the server that listens to all the different devices.")
        parser.add_argument('--list',
                            action='store_true',
                            help="List the currently available devices")
        parser.add_argument('--start',
                            action='store_true',
                            help="Start the server.")        
        args = parser.parse_args(sys.argv[2:])

        if not (args.list or args.start):
            return

        # init server        
        if args.list:
            list_devices()
        if args.start:
            run_server()
            

    def voice(self):

        parser = argparse.ArgumentParser(
            description="Interact with the voice stuff.")
        parser.add_argument('--models',
                            action='store_true',
                            help="List the currently available trained models")
        parser.add_argument('--list',
                            action='store_true',
                            help="List the current mapping from model to callback")
        parser.add_argument('--callbacks',
                            action='store_true',
                            help="List the currently available callbacks")
        parser.add_argument('--detect',
                            action='store_true',
                            required=False,                            
                            help="Start voice detection")
        parser.add_argument('--train',
                            action='store_true',
                            help="Train a new model.")
        parser.add_argument('--file',
                            nargs=3,
                            required=False,                            
                            help="Three .wav files to use for model trainig.")        
        args = parser.parse_args(sys.argv[2:])

        if args.detect:
            run_detection()
        if args.callbacks:
            print_available_callbacks()
        if args.models:
            print_available_models()
        if args.list:
            print_model_to_callback()
        if args.train:
            if args.file:
                train_new_model(wav_files=args.file)
            else:
                train_new_model()

    def lights(self):

        parser = argparse.ArgumentParser(
            description="Interact with the lights. Before doing anything, one has to call the register")
        parser.add_argument('command',
                            nargs='*',
                            help="Possible commands to the lights, has to be one of {}".format(LightsService.get_commands()))
        parser.add_argument('--register',
                            action='store_true',
                            help="Register yourself as a client to the Hue bridge.")
        parser.add_argument('--list',
                            action='store_true',
                            help="List the currently available lights.")        
        args = parser.parse_args(sys.argv[2:])

        if args.register:
            LightsService.register_hue_bridge()
        if args.list:
            LightsService.print_available_lights()

        # and finally dispense the command forward        
        if args.command:            
            LightsService.command(args.command[0], *args.command[1:])

        


def main():
    HomeCli()

if __name__ == "__main__":
    main()

    

    