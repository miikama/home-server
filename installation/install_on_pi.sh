#!/bin/bash

################### firewall ########################

# set up firewall 
sudo apt install ufw

# close ports
sudo ufw default deny incoming
sudo ufw default allow outgoing

# open ssh and http
sudo ufw allow ssh
sudo ufw allow http/tcp

# start firewall
sudo ufw enable

################## nginx ##############################

# install nginx
sudo apt update
sudo apt install nginx

# remove default nginx conf
sudo rm /etc/nginx/sites-enabled/default 
sudo rm /etc/nginx/sites-available/default 

# replace with our own configuration
sudo cp nginx.conf /etc/nginx/sites-available/homeserver
sudo ln -s /etc/nginx/sites-available/homeserver /etc/nginx/sites-enabled/homeserver

# restart nginx for effects to take place
sudo systemctl restart nginx


################# supervisor #################################

sudo apt install supervisor

# copy the template configuration
sudo cp supervisor.conf /etc/supervisor/conf.d/homeserver.conf

# initialize logfiles
sudo mkdir -p /var/log/homeserver
sudo touch /var/log/homeserver/error.log
sudo touch /var/log/homeserver/server.log

sudo supervisorctl reload



