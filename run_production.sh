#!/bin/bash

source henv/bin/activate
gunicorn -w 1 homeserver:app

