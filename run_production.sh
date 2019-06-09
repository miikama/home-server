#!/bin/bash

# get the application root directory (this script dir)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "running on $DIR"

# move to the application directory
cd $DIR

source henv/bin/activate
gunicorn -w 1 homeserver:app

