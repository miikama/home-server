import multiprocessing
import time
import enum
from typing import List

from homeserver.device_server import logger
from homeserver.voice_control.voice_service import VoiceService
from homeserver.light_control.lights_service import LightsService


class ServiceType(enum.Enum):
    INPUT = 1
    OUTPUT = 2
    INOROUT = 3


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

        # for each service that would want to listen to the events from the server
        # we need a separate queue
        self._output_event_queues = []

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

    def start_services(self, services):
        """
            Given a list of (services, service_types)
            
            Currently only VoiceService or LightsService

            The service type tells whether the service is an input or output.
            Input responds to outside events (such as voice detection)
            Output initiates outside events (such as putting lights on)

            There is currently a single multiprocessing.Queue for input events

            For each output service, own multiprocessing.Queue is created
        """

        for service, service_type in services:

            logger.info("Starting service {}".format(service.name))

            # initialise the service
            self._running_services[service.name] = service()

            queue = None
            if service_type == ServiceType.INPUT:
                queue = self.input_event_queue
            elif service_type == ServiceType.OUTPUT:
                self._output_event_queues.append(multiprocessing.Queue())
                queue = self._output_event_queues[-1]
            else:
                continue


            # start the service
            process = multiprocessing.Process(target=self._running_services[service.name].start_service,
                                              args=(queue,))

            # start the child process
            process.start()

            

    def start_loop(self):
        """
            loops until the end shutdown of the server

            listens to the Server input queue and processes messages
            that come in from started services.

            for each service that accepts events, sends the events to output queues
        """

        logger.info("Starting server event loop")

        while True: 

            msg = self._input_event_queue.get()

            logger.debug("Server got an event: {}".format(msg))

            for output_queue in self._output_event_queues:
                output_queue.put(msg)

            

def run_server():
    logger.info("Running device server")

    # get an instance of server
    server = Server()

    server.start_services([(VoiceService, ServiceType.INPUT),
                           (LightsService, ServiceType.OUTPUT)])

    logger.info("started all services")

    # start server loop
    server.start_loop()

    raise RuntimeError("Should not reach this")

    

def list_devices():
    print("No connected devices")


if __name__ == "__main__":
    run_server()