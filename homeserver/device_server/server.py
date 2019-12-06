import multiprocessing
import time

from typing import List

from homeserver.device_server import logger
from homeserver.voice_control.voice_service import VoiceService


class Server:



    """
        As one builds modules modules, one has to add decorators

        @server_input: 
            for functions that will given in a server event

        @server_listener: 
            for functions that can be invoked for server events

        to determine which inputs trigger which listeners, 
        a json-config file is read. (auto generated to default values)
        
    """


    # function name -> function
    _server_inputs = {}
    
    # the idea is to at most single running instance of Server
    _running_instance = None

    
    def __init__(self):
        
        logger.info("initializing server")
        if not Server._running_instance is None:
            raise RuntimeError("Only single server instance at a time supported")

        # set this instance to the current running
        Server._running_instance = self

        # initialize the incoming event queue from all child processes
        self._input_event_queue = multiprocessing.Queue()

        # keep track of services started
        self._running_services = {}

    @property
    def input_event_queue(self):
        return self._input_event_queue
    
    @staticmethod
    def get_running():
        return Server._running_instance

    def add_input(self, input_name, input_function):
        self._server_inputs[input_name] = input_function

    def server_input(self, input_name="test"):
        """

        """  
        def decorator(f):
            print("called decorator")            
            self.add_input(input_name, f)            
            print("server now has inputs: ", self._server_inputs)
            return f

        return decorator

    def start_services(self, services: List[VoiceService]):
        """
            Given a list of services (currently only of type VoiceService)
        """

        for service in services:

            logger.info("Starting service {}".format(service.name))

            # initialise the service
            self._running_services[service.name] = service()

            # start the service
            process = multiprocessing.Process(target=self._running_services[service.name].start_service,
                                              args=(self.input_event_queue,))

            # start the child process
            process.start()
            

    def start_loop(self):
        """
            loops until the end shutdown of the server

            listens to the Server input queue and processes messages
            that come in from started services.
        """

        logger.info("Starting server event loop")

        while True:

            print("Server got an event: ", self._input_event_queue.get())

            

def run_server():
    logger.info("Running device server")

    # get an instance of server
    server = Server()

    server.start_services([VoiceService])

    logger.info("started all services")

    # start server loop
    server.start_loop()

    raise RuntimeError("Should not reach this")

    

def list_devices():
    print("No connected devices")

    
# def server_input(func):
#     def wrapper():
#         print("called wrapper")
        
#         func()
#     return wrapper

    

if __name__ == "__main__":
    run_server()