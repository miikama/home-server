# home-server

## setup

the server is using python server library flask, install it with

```shell
pip install flask
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