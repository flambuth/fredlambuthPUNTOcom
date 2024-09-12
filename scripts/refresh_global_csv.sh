# Change to the 'archives' directory
cd /home/flambuth/fredlambuthPUNTOcom/data/global/

# Download the dataset using Kaggle CLI
/home/flambuth/.local/bin/kaggle datasets download --force asaniczka/top-spotify-songs-in-73-countries-daily-updated

# Unzip the downloaded file to the specified directory
unzip -o top-spotify-songs-in-73-countries-daily-updated.zip -d /home/flambuth/fredlambuthPUNTOcom/data/ref