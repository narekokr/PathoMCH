#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <folder_name>"
    exit 1
fi

FOLDER_NAME=$1

# Path to the service account key file
SERVICE_ACCOUNT_KEY="$HOME/mystic-torus-425820-p0-df4d7d0b777b.json"

# Authenticate with the service account
gcloud auth activate-service-account --key-file=$SERVICE_ACCOUNT_KEY

# Check if the authentication was successful
if [ $? -ne 0 ]; then
    echo "Failed to authenticate with service account."
    exit 1
fi

# Upload the folder to the specified GCS bucket
gsutil -m cp -r res/$FOLDER_NAME gs://dsitls-project/data/$FOLDER_NAME

# Check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Failed to upload the folder to GCS."
    exit 1
fi

echo "Folder $FOLDER_NAME successfully uploaded to gs://dsitls-project/data/$FOLDER_NAME"
