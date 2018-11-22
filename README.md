# home-server



## complete setup

Dependencies for pyaudio

```shell
sudo apt-get install portaudio19-dev python-all-dev
```
Get virtualenvironment

```shell
sudo pip install --upgrade virtualenv
```

sudo install virtualenv for it to go to /usr/local/bin. Can be installed for just the current user as well. Activate environment

```shell
virtualenv --python python3 henv
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

Install the atlas matrix computing library and sox

```shell sudo apt-get install sox libatlas-base-dev ```

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



## setup

### running locally and the firewall rules

On Raspberry pi 3 ssh is disabled by default. Go to Settings-> Raspberry Pi Configuration -> Interfaces -> enable ssh. Restrict the access to the device to only local network by adding a tcp. 

In a file /etc/hosts.deny, add line ´´´shell ALL : ALL´´´ To deny all incoming connections. 

In file /etc/hosts.allow, add line  ´´´shell sshd : 192.168.0. ´´´ to add an exception and allow ssh connections from local subnet.

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