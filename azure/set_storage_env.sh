#!/bin/bash

#Configuration
RESOURCE_GROUP="anomaly_detection"
STORAGE_ACCOUNT ="llamamlws6782360884"


# Fetch and export the connection string 
AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
--name "$STORAGE_ACCOUNT" \
--resource-group "$RESOURCE_GROUP" \
--output tsv)


if [-z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo " Failed to retrieve connection string for $STORAGE_ACCOUNT"
    exit 1
fi
# Export the connection string to the current shell session
export AZURE_STORAGE_CONNECTION_STRING

echo "AZURE_STORAGE_CONNECTION_STRING set for storage account: $STORAGE_ACCOUNT"