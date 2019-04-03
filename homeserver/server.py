
from flask import render_template, url_for, flash, redirect, jsonify
from homeserver import app
import requests


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error404.html', title="404"), 404


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/devices", methods=["GET"])
def devices():	
	#TODO could return the last known state of the devices
	interfaces = app.device_handler.interfaces
	print([inf.name for inf in interfaces])
	print([inf.is_on for inf in interfaces])
	print([inf.connected for inf in interfaces])
	print([inf.devices for inf in interfaces])

	return render_template('devices.html', interfaces=interfaces, title="Devices")

@app.route("/devices/<device_id>/<command>/<arguments>", methods=["POST"])
def device_status(device_id, command, arguments):
	device_id = str(device_id)
	command = str(command)
	arguments = str(arguments).split('&')
	device = app.device_handler.handle_action(device_id, command, arguments)
	if not device:				
		flash('No success', 'danger')
	#get the updated state of the devices
	interface = app.device_handler.interfaces
	return devices()
	


@app.route('/device_action/<interface_id>/<action>'				, methods=["POST"])
@app.route('/device_action/<interface_id>/<device_id>/<action>' , methods=["POST"])
def device_action(interface_id, action, device_id=None):
	"""
		Main interface point
	"""
	interface_id = str(interface_id)

	if device_id is not None:
		device_id = str(device_id) # to string
	if action is not None:
		action = str(action) 	#  to string

	print("interface id: ", interface_id)
	print("device id: ", device_id)


	app.device_handler.handle_action(interface_id=interface_id, action_name=action,  device_id=device_id )

	# return 
	status_dict =app.device_handler.get_status_json()

	print("returning status: ", status_dict)

	return jsonify(status_dict)

@app.route("/status", methods=["POST"])
def status():
	return jsonify(app.device_handler.get_status_json())

