
from flask import render_template, url_for, flash, redirect, jsonify
from homeserver import device_handler,app
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
	interfaces = device_handler.interfaces
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
	device = device_handler.handle_action(device_id, command, arguments)
	if not device:				
		flash('No success', 'danger')
	#get the updated state of the devices
	interface = device_handler.interfaces
	return devices()
	


#
@app.route("/<deviceId>/<action>", methods=["POST"])
def device_action(deviceId, action):
	# Convert the device id from the URL into a string	
	device_id = str(deviceId)
	action_name = str(action) 	#  cast into string
	#let the device handler handle the action	
	device = device_handler.handle_action(device_id, action_name)
	
	if not device:				
		flash('No success', 'danger')
	return redirect(url_for('devices'))


