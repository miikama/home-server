
from flask import Flask, render_template, url_for, flash, redirect
from device_handler import DeviceHandler
from forms import DeviceOnForm
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

device_handler = DeviceHandler( os.path.join( os.path.dirname(os.path.realpath(__file__)), 'device_configs')    )


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
		#flash('{} has been toggled'.format(device.nice_name), 'success')	
		flash('No success', 'danger')
	return redirect(url_for('devices'))




if __name__ =="__main__":
	app.run(debug=True)
