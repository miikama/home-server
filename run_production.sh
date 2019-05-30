#!/bin/bash

source henv/bin/activate

# binding the server to 0.0.0.0 exposes the server to connections in the same network
gunicorn -w 1 -b 0.0.0.0:8000 homeserver:app

