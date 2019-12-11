# Home-server

Home-server is a simple server built on Python. You can use Home-server to:

#### Detect

keywords with an offline keyword-detection. This detection is based on models from [Snowboy](https://snowboy.kitt.ai/). Home-server also comes with a command-line interface (CLI) for training custom own hotwords. 

#### Interact 
with your home's Philip's Hue smart lights. The detected keywords can be linked to different light commands.

#### Notes for installation and usage 

- [Installation](##Installation)
- [Getting Started](##Getting-started)
- [Notes on setup](##Complete-setup)


This work is licensed under the MIT license. Note that code under Snowboy follows a separate license.

## Installation

Home-server is not yet available in [PyPI](https://pypi.org/), so easiest way to install is to clone this repository.

```shell
git clone https://github.com/miikama/home-server.git
cd home-server
```

And create a Python virtual environment

```
python -m venv henv
source henv/bin/activate
python setup.py develop
```

The snowboy modules will have to be installed manually. They can be installed with

```
cd installation
./install_snowboy.sh
```

The installation requires sudo if you do not have swig installed. Swig creates Python wrappers for the keyword detector written in C++.

## Getting started

After installing inside a Python virtual environment (and with the environment active) the CLI is available under the alias hserv.

### CLI

```shell
(henv) anon:home-server$ hserv -h

usage: 

hserv <command-name> [arguments]

command-name can be:
    voice   [voice-args]            
    devices [device-args]  
    lights [light-args]          

A common entrypoint for multiple different command line tools

positional arguments:
  command     Command is any of the following: ('voice', 'devices', 'lights')

optional arguments:
  -h, --help  show this help message and exit

```

### Voice control

The voice-control related commands are under hserv voice. 

```shell
hserv voice -h
usage: hserv [-h] [--models] [--list] [--callbacks] [--detect] [--train]
             [--file FILE FILE FILE]

Interact with the voice stuff.

optional arguments:
  -h, --help            show this help message and exit
  --models              List the currently available trained models
  --list                List the current mapping from model to callback
  --callbacks           List the currently available callbacks
  --detect              Start voice detection
  --train               Train a new model.
  --file FILE FILE FILE
                        Three .wav files to use for model trainig.
```

- --train can be used to train a new model with the Snowboy api
- --callbacks show the available actions for voice commands. 
- --list shows what callbacks the current trained keyword-models are mapped to (what happes for each keyword detected)
- --detect runs the voice detection and can be used to test the trained models.

The decision what the models are mapped to can be found in home-server/homeserver/server.ini

### Philips Hue lights

The command line tool can be used to control you home smart lights as well.

```shell
usage: hserv [-h] [--register] [--list] [--schedules] [command [command ...]]

Interact with the lights. Before doing anything, one has to call the register

positional arguments:
  command      Possible commands to the lights, has to be one of ('on', 'off',
               'level', 'start_schedule')

optional arguments:
  -h, --help   show this help message and exit
  --register   Register yourself as a client to the Hue bridge.
  --list       List the currently available lights.
  --schedules  List the currently existing schedules in the bridge.
```

The first command for the lights has to be --register. This requires pushing a physical button in the philips Hue bridge for registering a new user.

### Start the server

After connecting lights and setting up the voice commands you can start the server with devices --start and leave it running.

```shell
usage: hserv [-h] [--list] [--start]

The CLI for the server that listens to all the different devices.

optional arguments:
  -h, --help  show this help message and exit
  --list      List the currently available devices
  --start     Start the server.
```

The installation folder has a script 'install_on_pi.sh' which install supervisor and sets up a supervisor job for automatically starting the homeserver on computer startup. This continuous mode logs can be found under /var/log/homeserver.

## Additional notes :)

### complete setup

Dependencies for pyaudio

```shell
sudo apt-get install portaudio19-dev python-all-dev
```
Create and activate python virtualenvironment (For python < 3.5? one has to install virtualenvironment separately)

```shell
python3 -m venv henv
source henv/bin/activate
```

Once the virtual environment is active, install dependencies

```shell
pip install --upgrade pyaudio flask google-cloud-speech phue
```

Deactivate virtual environment with 

```shell
deactivate
```

Check install instructions for snowboy on https://github.com/Kitt-AI/snowboy. Needs swig 3.0.10 installed. Here a copy of the instructions at the time

Install the atlas matrix computing library and sox. AND Pulseaudio (not mentioned in snowboy requirements but was needed in Raspberry Pi)

```shell
sudo apt-get install sox libatlas-base-dev pulseaudio
```

Compile a supported swig version (3.0.10 or above)

```shell 
wget http://downloads.sourceforge.net/swig/swig-3.0.10.tar.gz
sudo apt-get install libpcre3 libpcre3-dev
./configure --prefix=/usr                  \
        --without-clisp                    \
        --without-maximum-compile-warnings &&
make
make install &&
install -v -m755 -d /usr/share/doc/swig-3.0.10 &&
cp -v -R Doc/* /usr/share/doc/swig-3.0.10
```



Update the path to google API credentials and your own Snowboy model in a file server.ini. Use server.example.ini as a basis.

## Running a production server on pi

The actual server is run on gunicorn, which is easily installed with

```shell
pip install gunicorn
```

To provide the local net devices access to the server, an application nginx is used. It can be installed with 

```shell
sudo apt install nginx
```

Check the shell scripts 'install_on_pi.sh' and 'run_production.sh'.


## setup

### running locally and the firewall rules

On Raspberry pi 3 ssh is disabled by default. Go to Settings-> Raspberry Pi Configuration -> Interfaces -> enable ssh. Restrict the access to the device to only local network by adding a tcp. 

In a file /etc/hosts.deny, add line ```shell ALL : ALL``` To deny all incoming connections. 

In file /etc/hosts.allow, add line  ```shell sshd : 192.168.0.``` to add an exception and allow ssh connections from local subnet.

### parts

the server is using python server library flask, install it with

```shell
pip install flask

```

### installing the google cloud api

```shell

pip install --upgrade virtualenv

virtualenv --python python3 env

source env/bin/activate

pip install google-cloud-storage
pip install --upgrade google-cloud-speech

```

stop using virtualenv

```shell
deactivate

```

### recording sound with microphone

use pyaudio python library

list devices

```shell
lsusb -t
```

pyaudio uses the system default input device

### using sphinx (not used)

dependencies 

```shell
sudo apt-get install swig libpulse-dev libasound2-dev	
pip install --upgrade pocketsphinx
```

full list

```shell
sudo apt-get install -qq python python-dev python-pip build-essential swig git libpulse-dev libasound2-dev
```


## General concept

* a flask server running on rasperry pi and connected to home smart devices

* server is accessible in a browser in the local wifi

* keep record of all the available home devices as objects and directly store the objects
  
  each device has it's own config file

  there is an object for each possible device 

  device objects hold the routines for installing the device and communicating with the device


* data input streams 
	
  Light level

  sound level

* functions on the devices that take in a general input stream

  e.g light object has takes intensity as input, set the output of sound level to the input



## Ideas

* user authentication with pressing a button on rasperry



## The api for the web interface

possible post requests 

```shell
commands: ['is_on':boolean]
```

the structure of a possible json representation of the state of all the interfaces the interface 

```python
{'data': [interface1, interface2, ...]}

{'data': 
[
{
'name': string,
'connected': boolean,
'is_on': boolean,
'devices': [{'location':string,
			'nice_name': string,
			'full_name': string,
			'location': string,
			'id': string,
			'is_on': boolean,
			'enabled': boolean }]
},
interface2, ...
]
}
```
```python
{}
```

### snowboy

snowboy offers compiled source for python2. For python3 the source has to be compiled yourself

```shell
git clone https://github.com/Kitt-AI/snowboy.git
cd swig/Python3
make
```

copy
- snowboy/swig/Python3/* into <home-server-dir>/snowboy 
- snowboy/resources/{common.res, ding.vaw, dong.vaw} into <home-server-dir>/snowboy/resources
- snowboy/examples/Python/{snowboydecoder.py,snowboythreaded.py} into <home-server-dir>/snowboy
- your model into <home-server-dir>/snowboy/resources