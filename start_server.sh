#!/bin/bash

# Change to project directory
cd /home/ubuntu/deep-brochures

# Activate virtual environment
source venv/bin/activate

# Start gunicorn server
exec gunicorn main:app -c gunicorn.conf.py 