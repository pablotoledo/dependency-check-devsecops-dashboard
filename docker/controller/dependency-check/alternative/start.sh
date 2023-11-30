#!/bin/bash
set -e
set -x

# We have 3 environment variables to configure the dependency-check:
# - GITHUB_URL (required): the URL of the GitHub repository to scan with the valid token
# - GITHUB_REPO_NAME (required): the name of the GitHub repository to scan
# - NVD_API_KEY (optional): the API key to use the NVD database

# Clone the repository
git clone $GITHUB_URL $GITHUB_REPO_NAME

# Move to the repository
cd $GITHUB_REPO_NAME

# Run the dependency-check
dependency-check --project "test" --scan "." --format "JSON" --format "HTML" --out "." --enableExperimental  --noupdate

# Check if $GITHUB_REPO_NAME folder exists at /data and if not then create it
if [ ! -d "/data/$GITHUB_REPO_NAME" ]; then
  mkdir -p /data/$GITHUB_REPO_NAME
fi

# Create a folder in /data/$GITHUB_REPO_NAME with the current datetime
folder=$(date +%Y-%m-%d_%H-%M-%S)
mkdir -p /data/$GITHUB_REPO_NAME/$folder

# Copy the dependency-check reports to the folder
#cp dependency-check-report.json /data/$GITHUB_REPO_NAME/$folder
#cp dependency-check-report.html /data/$GITHUB_REPO_NAME/$folder

#sleep 600

# Verificar que el archivo JSON existe y luego procesarlo
if [ -f "dependency-check-report.json" ]; then
    echo "Found dependency-check-report.json, processing..."
    python3 ../feed_mongo.py "$(pwd)/dependency-check-report.json" "$GITHUB_REPO_NAME"
else
    echo "El archivo JSON no se encontró."
fi

#sleep 25