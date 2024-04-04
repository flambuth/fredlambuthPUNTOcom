#!/bin/bash

# Set the path to your virtual environment directory
VENV_DIR="/home/flambuth/fredlambuthPUNTOcom/fredlambuth_env"

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
    # Use Python interpreter from the virtual environment
    "$VENV_DIR/bin/python3" /home/flambuth/fredlambuthPUNTOcom/spotify_jobs_rp.py
else
    # Fallback to using system Python interpreter
    /usr/bin/python3 /home/flambuth/fredlambuthPUNTOcom/spotify_jobs_rp.py
fi
