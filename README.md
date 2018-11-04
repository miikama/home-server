# home-server



## complete setup




```shell
pip install --upgrade virtualenv
virtualenv --python python3 henv
source henv/bin/activate
```

pyaudio

```shell
sudo apt-get install portaudio19-dev
sudo apt-get install  python-all-dev
pip install pyaudio 
pip install flask
pip install google-cloud-storage
pip install --upgrade google-cloud-speech
```








## setup



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

should find microphone with type class audio and driver snd-usb-audio

first 

```shell
sudo apt-get install portaudio19-dev
sudo apt-get install  python-all-dev
```

then

```shell
pip install pyaudio 
```

or 

```shell
 sudo apt-get install python-pyaudio python3-pyaudio 
 ```

pyaudio seems to record the system default audio device


### using sphinx

dependencies 

```shell
sudo apt-get install swig libpulse-dev libasound2-dev	
pip install --upgrade pocketsphinx
```

full list

```shell
sudo apt-get install -qq python python-dev python-pip build-essential swig git libpulse-dev libasound2-dev
```


### Speechrecognition

```shell
pip install SpeechRecognition
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