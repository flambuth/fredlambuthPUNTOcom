#!/bin/bash

# Set the path to your virtual environment directory
VENV_DIR="/home/flambuth/fredlambuthPUNTOcom/fredlambuth_env"
PROJECT_DIR="/home/flambuth/fredlambuthPUNTOcom"

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
    cd "$PROJECT_DIR"
    export PYTHONPATH="$PROJECT_DIR"
    # Use Python interpreter from the virtual environment
    "$VENV_DIR/bin/python3" scripts/archiving_records.py
else
    # Fallback to using system Python interpreter
    export PYTHONPATH="$PROJECT_DIR"
    /usr/bin/python3 "$PROJECT_DIR/scripts/archiving_records.py"
fi