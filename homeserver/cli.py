import sys
import argparse

from homeserver.voice_control.model_service import print_available_models, train_new_model


class HomeCli:

    '''
        A common entrypoint for multiple different command line tools
    '''

    cli_commands = ('voice')

    def __init__(self):

        parser = argparse.ArgumentParser(
            description="A common entrypoint for multiple different command line tools",
            usage=''' hserv command-name arguments
            command-name can be:
                voice [voice-args]            
            ''')       

        parser.add_argument('command',
                            help="Command is any of the following: {}".format(self.cli_commands))

                                    
        args = parser.parse_args(sys.argv[1:2])
        
        if args.command not in self.cli_commands:
            parser.print_help()
            sys.exit(1)

        # if the argument is marked as a possible command,
        # A method with the same name is invoked
        getattr(self, args.command)()
            

    def voice(self):

        parser = argparse.ArgumentParser(
            description="Interact with the voice stuff.")
        parser.add_argument('--list',
                            action='store_true',
                            help="List the currently available trained models")
        parser.add_argument('--train',
                            action='store_true',
                            help="Train a new model.")
        parser.add_argument('-f', '--files',
                            nargs=3,
                            required=False,                            
                            help="Three .wav files to use for model trainig.")
        args = parser.parse_args(sys.argv[2:])

        if args.list:
            print_available_models()
        if args.train:
            if args.files:
                train_new_model(wav_files=args.files)
            else:
                train_new_model()


def main():
    HomeCli()

if __name__ == "__main__":
    main()

    

    