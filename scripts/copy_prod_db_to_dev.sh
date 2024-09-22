#!/bin/bash

PROJECT_DIR="/home/flambuth/fredlambuthPUNTOcom"
ARCHIVE_DIR="/home/flambuth/archives"

cd "$PROJECT_DIR"
scp "flambuth@flask_site:$PROJECT_DIR/data/fred.db" "$ARCHIVE_DIR/fred_dbs/"
scp "flambuth@flask_site:$PROJECT_DIR/data/global.db" "$ARCHIVE_DIR/global/"