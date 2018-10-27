
from flask import render_template, url_for, flash, redirect
from homeserver import device_handler,app


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error404.html', title="404"), 404


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/devices", methods=["GET", "POST"])
def devices():
	return render_template('devices.html', devices=device_handler.devices, title="Devices")
	

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


