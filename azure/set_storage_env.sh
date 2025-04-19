#!/bin/bash

# Manually defined variables
STORAGE_ACCOUNT="llamamlws6782360884"
RESOURCE_GROUP="anomaly_detection"

# Get the connection string
AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query connectionString \
  --output tsv)

# Check if the command succeeded
if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
  echo "Failed to retrieve connection string for $STORAGE_ACCOUNT"
  return 1
fi

# Export the connection string
export AZURE_STORAGE_CONNECTION_STRING
echo "AZURE_STORAGE_CONNECTION_STRING set for storage account: $STORAGE_ACCOUNT"