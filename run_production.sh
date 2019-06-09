#!/bin/bash

# get the application root directory (this script dir)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "running on $DIR"

# move to the application directory
cd $DIR

source henv/bin/activate

# binding the server to 0.0.0.0 exposes the server to connections in the same network
gunicorn -w 1 -b 0.0.0.0:8000 homeserver:app

