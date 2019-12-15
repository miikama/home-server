
import threading
import time
import requests
import os
import enum
import multiprocessing

from phue import Bridge, PhueRegistrationException, PhueRequestTimeout

from homeserver import config
from homeserver.light_control import logger, LIGHT_CONTROL_DIR

class LightLevel(enum.Enum):
    LOW = 1
    MID = 2
    HIGH = 3

    @staticmethod
    def to_string():
        return "levels: " + (", ".join([ level.name for level in LightLevel]))

class LightColor(enum.Enum):
    RED = 1
    BLUE = 2
    WHITE = 3

    @staticmethod
    def to_string():
        return "colors: " + (", ".join([ level.name for level in LightColor]))


class LightsService:

    name = "Philips Lamp Bridge"
    
    def __init__(self):

        # do not register a new bridge in initialiazation
        if not LightsService.registered_succesfully():
            raise RuntimeError("Use hserv lights --register to set up a new bridge before running server.")

        #dont connect to the bridge in the initialization because can timeout, 
        #this will be done first time there is a call to the lights
        self.bridge = LightsService.connect_to_hue_bridge(LightsService.light_config())

        self._event_queue = None

    def start_service(self, event_queue: multiprocessing.Queue):
        logger.info("Starting light service")

        self._event_queue = event_queue

        while True:

            event = self._event_queue.get()

            logger.info("lights got message {}".format(event))

            if event.msg == "lights_on":
                self.lights_on()
            if event.msg == "lights_off":
                self.lights_off()
            if event.msg == "dim_lights":
                self.set_light_level(LightLevel.LOW)            
            if event.msg == "bright_lights":
                self.set_light_level(LightLevel.HIGH)
            if event.msg == "start_schedule":
                self.start_schedule()
                self.set_light_color(LightColor.RED)


        raise RuntimeError("Should not get here.")
    

    def lights_on(self):            
        if self.bridge is None:
            return

        #get the lights from hue bridge as phue Light objects
        lights = self.bridge.get_light_objects()

        for light in lights:
            self.bridge.set_light(light.light_id, 'on', True)

    def lights_off(self):            
        if self.bridge is None:
            return

        #get the lights from hue bridge as phue Light objects
        lights = self.bridge.get_light_objects()

        for light in lights:
            self.bridge.set_light(light.light_id, 'on', False)

    def set_light_level(self, level: LightLevel):	
        if self.bridge is None:
            return

        brightness = 0

        if level == LightLevel.LOW:
            brightness = 30
        elif level == LightLevel.MID:
            brightness = 127
        elif level == LightLevel.HIGH:
            brightness = 200
        else:
            return
        
        logger.info("Setting light level to {}".format(brightness))	

        for light in self.bridge.get_light_objects():
            self.bridge.set_light(light.light_id, 'bri', brightness)

    def set_light_color(self, color: LightColor):	
        """
            Colors are defined with values based on 
            https://developers.meethue.com/develop/get-started-2/core-concepts/
        """

        if self.bridge is None:
            return

        xy = [0,0]
        if color == LightColor.WHITE:
            xy = [0.4, 0.4]
        elif color == LightColor.BLUE:
            xy = [0.2, 0.3]
        elif color == LightColor.RED:
            xy = [0.6, 0.4]
        else:
            return
        
        logger.info("Setting light color to {}".format(xy))	

        for light in self.bridge.get_light_objects():
           self.bridge.set_light(light.light_id, {
               'xy': xy, 
           })
    
    def start_schedule(self):
        """
            takes the schedule that is marked as the currently
            active in configuration and starts it
        """
        if self.bridge is None:
            return

        schedule_id, schedule_name  = self.get_active_schedule()

        logger.info("starting schedule: {}".format(schedule_name))

        attributes = {
            'status': 'enabled'
        }

        response = self.bridge.set_schedule_attributes(schedule_id, attributes)
        
        if 'error' in response[0]:
            logger.info("Starting schedule failed: {}".format(response[0]))
        elif 'success' in response[0]:
            logger.info("Starting schedule succeeded.")
        
        
    def get_active_schedule(self):                
        for group_id, group in self.bridge.get_schedule().items():
            # currently one schedule can be controlled 
            schedule_name = group.get('name')
            active_name = LightsService.get_active_schedule_name()
            if schedule_name == active_name:
                return group_id, active_name
            
        return -1, ""

    @staticmethod
    def get_active_schedule_name():
        """
            the schedule that is marked active in configuration
        """
        return config['LIGHTS'].get('controlled_schedule')

    @staticmethod
    def connect_to_hue_bridge(config):
        """	function to establish a connection to the hue bridge """

        logger.info("Connecting to hue bridge")

        bridge = None
            

        max_connect_tries = 3		
        for i in range(max_connect_tries):
            try:				
                #get the dridge	
                bridge = Bridge(config['hue_bridge_ip'], config_file_path=config['hue_config_file'])
                # actually do an api request to check whether the connection was succesfull
                bridge.get_light_objects()
                logger.info("Connected to hue bridge")
                # self.connected = True	
                # self.is_on = True			
                break
            except PhueRegistrationException:
                print("\npush the button on the hue bridge, waiting 15 sec for {}:th attempt out of {}\n".format(i+1, max_connect_tries))
                time.sleep(15)	
            except PhueRequestTimeout:
                #actually cannot timeout because initialising bridge does not check whether hue bridge is available
                print("[ ERROR  ] Cannot connect to HUE bridge")
                bridge = None
                break

        return bridge

    @staticmethod
    def light_config():
        if 'LIGHTS' in config:            
            return config['LIGHTS']
        return {}

    @staticmethod
    def update_light_configuration(config):        

        light_config = {
            'hue_bridge_ip': '',
			'hue_config_file': os.path.join(LIGHT_CONTROL_DIR, 'hue.conf'), 
            'controlled_schedule': ''
        }

        if 'LIGHTS' in config:
            light_config.update(config['LIGHTS'])

        return light_config

    @staticmethod
    def get_hue_bridge_ip():
        """
            Uses a UPnP discovery provided by Philips Hue. 

            see https://huetips.com/help/how-to-find-my-bridge-ip-address/

            basically makes a get request to an api endpoint, which then 
            does some JS magic to find Hue bridges in the local network
        """

        api_address = "https://www.meethue.com/api/nupnp"
    
        response = requests.get(api_address)

        data = response.json()

        # no devices found
        if len(data) == 0:
            return ""

        # I guess one can have multiple bridges in the same network, take the first
        data = data[0]

        if 'id' in data and 'internalipaddress' in data:
            return data['internalipaddress']
        
        return ""
        
    @staticmethod
    def registered_succesfully():
        if 'LIGHTS' in config:
            if 'hue_bridge_ip' in config['LIGHTS']:
                return True

        return False

    @staticmethod
    def get_commands():
        return ('on','off','level', 'start_schedule', 'color')

    @staticmethod
    def command(name, *args):
        """
            Entry point for commanding lights
        """

        if not LightsService.registered_succesfully():
            print("Register the hue bridge first with lights --register")
            return

        if name not in LightsService.get_commands():
            logger.info("Light command {} not found".format(name))
            return

        service = LightsService()

        # call the correct function
        logger.debug("calling light command {} with args {}".format(name, args))

        if name == 'on':
            service.lights_on()
        elif name == 'off':
            service.lights_off()
        elif name == 'start_schedule':
            service.start_schedule()
        elif name == 'level':
            # level requires an extra argument which denotes the light level, one of (LOW, MID, HIGH)
            if len(args) > 0 and args[0] in [level.name for level in LightLevel]:
                service.set_light_level(LightLevel[args[0]])
            else:
                logger.info("When setting light level, argument has to be one of {}".format(LightLevel.to_string()))
        elif name == 'color':            
            # color requires an extra argument which denotes the light color, type LightColor            
            if len(args) > 0 and args[0] in [color.name for color in LightColor]:
                service.set_light_color(LightColor[args[0]])
            else:
                logger.info("When setting light color, argument has to be one of {}".format(LightColor.to_string()))
        


    @staticmethod
    def print_available_schedules():

        if not LightsService.registered_succesfully():
            print("Register the hue bridge first with lights --register")
            return

        service = LightsService()

        print("\nAvailable schedules:\n")
        for group_id, group in service.bridge.get_schedule().items():
            # currently one schedule can be controlled 
            schedule_name = group.get('name')
            active_name = LightsService.get_active_schedule_name()
            active_string = "ACTIVE" if schedule_name == active_name else ""
            print("%-30s with id: %2s %10s" % (schedule_name, group_id, active_string))
        
        print("")


    @staticmethod
    def print_available_lights():

        if not LightsService.registered_succesfully():
            print("Register the hue bridge first with lights --register")
            return

        service = LightsService()

        print("\nAvailable lights:\n")
        for light in service.bridge.get_light_objects():
            print("%-30s with id: %s." % (light.name, light.light_id))
            

        print("\nAvailable groups:\n")
        for group_id, group in service.bridge.get_group().items():
            print("%-30s with id: %s." % (group.get('name'), group_id))
        
        print("")

    @staticmethod
    def register_hue_bridge():
        """
            If no hue ip is provided in the server configuration file
            Tries to find the hue bridge.

            After that tries to connect to Hue bridge.

            If the connection is the first for this Hue bridge 
            or the Hue configuration file is missing, tries to register 
            a new user with the Hue bridge. 
            
            Registering a new device with the bridge requires pushing a
            physical button on the actual Hue bridge.
        """
        
        print("\nRegistering device with the Hue bridge\n")    

        light_config = config['LIGHTS']
        hue_bridge_ip = light_config['hue_bridge_ip']

        # if the ip is not set try to find the bridge
        if not hue_bridge_ip:

            print("\nNo Hue bridge ip in configuration file, trying to find Hue bridge\n")

            hue_bridge_ip = LightsService.get_hue_bridge_ip()
            if not hue_bridge_ip:
                print("Could not find a Philips Hue bridge...")
                return
            print("Hue bridge found.")
        else:
            print("A previous Hue bridge ip found.")
        
        
        print("Using Hue bridge at ip: '{}'\n".format(hue_bridge_ip))    
        light_config['hue_bridge_ip'] = hue_bridge_ip

        # try to connect
        bridge = LightsService.connect_to_hue_bridge(light_config)

        # if registering is succesfull, update configuration
        if bridge:
            config.add_configuration_parameters("LIGHTS", light_config)
        # if not, do not update configuration
        else:
            print("Registering failed")

    
    
if __name__ == "__main__":
    LightsService.print_available_lights()