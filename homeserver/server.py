
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


@app.route("/devices", methods=["GET", "POST"])
def devices():	
	#TODO could return the last known state of the devices
	interfaces = device_handler.interfaces
	print([inf.name for inf in interfaces])
	print([inf.is_on for inf in interfaces])
	print([inf.connected for inf in interfaces])
	print([inf.devices for inf in interfaces])
	
	return render_template('devices.html', interfaces=interfaces, title="Devices")


@app.route("/update_device", methods=["POST"])
def update_device():
	print(requests.form)
	device_id = requests.form.get('device_id')
	device = device_handler.get_device(device_id)
	if device:	
		return render_template('device.html', device=device)
	else:
		return jsonify({'device':'not_found'})



@app.route("/update_devices", methods=["POST"])
def update_devices():	
	""" separate function to asynchronously get the current states of the devices"""
	return jsonify({'devices':self.device_handler.devices})


	

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


