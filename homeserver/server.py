
from flask import render_template, url_for, flash, redirect, jsonify, Blueprint
from homeserver import logger

from homeserver.device_server.server import Server as DeviceServer


device_handler = DeviceServer.get_running()



api_routes = Blueprint("api", __name__)


@api_routes.errorhandler(404)
def not_found_error(error):
    return render_template('error404.html', title="404"), 404


@api_routes.route("/")
@api_routes.route("/home")
def home():
    return render_template('home.html')


@api_routes.route("/devices", methods=["GET"])
def devices():	
	#TODO could return the last known state of the devices
	interfaces = device_handler.interfaces
	print([inf.name for inf in interfaces])
	print([inf.is_on for inf in interfaces])
	print([inf.connected for inf in interfaces])
	print([inf.devices for inf in interfaces])

	return render_template('devices.html', interfaces=interfaces, title="Devices")

@api_routes.route("/devices/<device_id>/<command>/<arguments>", methods=["POST"])
def device_status(device_id, command, arguments):
	device_id = str(device_id)
	command = str(command)
	arguments = str(arguments).split('&')
	device = device_handler.handle_action(device_id, command, arguments)
	if not device:				
		flash('No success', 'danger')
	#get the updated state of the devices
	interface = device_handler.interfaces
	return devices()
	


@api_routes.route('/device_action/<interface_id>/<action>'				, methods=["POST"])
@api_routes.route('/device_action/<interface_id>/<device_id>/<action>' , methods=["POST"])
def device_action(interface_id, action, device_id=None):
	"""
		Main interface point
	"""
	interface_id = int(interface_id)

	if device_id is not None:
		device_id = int(device_id) # to string
	if action is not None:
		action = str(action) 	#  to string

	logger.info("interface id: {}".format(interface_id))
	logger.info("device id: {}".format(device_id))
	logger.info("action: {}".format(action))


	device_handler.handle_action(interface_id=interface_id, action_name=action,  device_id=device_id )

	status_dict =device_handler.get_status_json()

	return jsonify(status_dict)

@api_routes.route("/status", methods=["POST"])
def status():
	return jsonify(device_handler.get_status_json())
