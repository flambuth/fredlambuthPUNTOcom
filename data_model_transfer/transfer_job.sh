#!/bin/bash

cd /home/flambuth/new_fred

# Run Flask-Migrate to upgrade the database
flask db upgrade
mv fred.db data_model_transfer/

# Check if Flask-Migrate upgrade was successful
if [ $? -eq 0 ]; then
    echo "Flask-Migrate upgrade completed successfully."
else
    echo "Error: Flask-Migrate upgrade failed."
    exit 1
fi

cd data_model_transfer
# Execute SQL script to transfer data
sqlite3 fred.db < transfer.sql

# Check if SQL script execution was successful
if [ $? -eq 0 ]; then
    echo "Data transfer completed successfully."
else
    echo "Error: Data transfer failed."
    exit 1
fi

cp fred.db ../fred.db

echo "Script execution completed."
