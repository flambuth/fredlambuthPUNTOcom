#!/bin/bash

# Set the path to your virtual environment directory
VENV_DIR="/home/flambuth/fredlambuthPUNTOcom/fldotcom_dev_env"
PROJECT_DIR="/home/flambuth/fredlambuthPUNTOcom"

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
    cd "$PROJECT_DIR"
    export PYTHONPATH="$PROJECT_DIR"
    "$VENV_DIR/bin/python3" cron_jobs/spotify_jobs_daily.py
else
    # Fallback to using system Python interpreter
    export PYTHONPATH="$PROJECT_DIR"
    /usr/bin/python3 "$PROJECT_DIR/cron_jobs/spotify_jobs_daily.py"
fi