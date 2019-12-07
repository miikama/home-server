#!/bin/bash



# get the application directory root path
dir=$(pwd)
app_root="$(dirname "$dir")"

# install for current user
cur_user=$(whoami)

echo "Using app root directory $app_root, installing for user $cur_user"


################### firewall ########################

# # set up firewall 
# sudo apt install ufw

# # close ports
# sudo ufw default deny incoming
# sudo ufw default allow outgoing

# # open ssh and http
# sudo ufw allow ssh
# sudo ufw allow http/tcp

# # start firewall
# sudo ufw enable

################## nginx ##############################

# # install nginx
# sudo apt update
# sudo apt install nginx

# # remove default nginx conf
# sudo rm /etc/nginx/sites-enabled/default 
# sudo rm /etc/nginx/sites-available/default 

# # set the correct app paths to template
# sed "s:/path/to/server:${app_root}:g" nginx.conf.template > nginx.conf

# # replace with our own configuration
# sudo cp nginx.conf /etc/nginx/sites-available/homeserver
# sudo ln -s /etc/nginx/sites-available/homeserver /etc/nginx/sites-enabled/homeserver

# # restart nginx for effects to take place
# sudo systemctl restart nginx


################# supervisor #################################

sudo apt install supervisor

# set the correct app paths to template
sed "s:/path/to/server:${app_root}:g" supervisor.conf.template > supervisor.conf
# start the supervisor job under the current user
sed -i "s:/my/user:${cur_user}:g" supervisor.conf

# copy the template configuration
#sudo cp supervisor.conf /etc/supervisor/conf.d/homeserver.conf

# initialize logfiles
#sudo mkdir -p /var/log/homeserver
#sudo touch /var/log/homeserver/error.log
#sudo touch /var/log/homeserver/server.log

#sudo supervisorctl reload



