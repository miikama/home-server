
from flask import Flask, render_template
from device_handler import DeviceHandler
import os


app = Flask(__name__)

device_handler = DeviceHandler( os.path.join( os.path.dirname(os.path.realpath(__file__)), 'device_configs')    )


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/devices")
def devices():
	return render_template('devices.html', devices=device_handler.devices, title="Devices")



if __name__ =="__main__":
	app.run(debug=True)
