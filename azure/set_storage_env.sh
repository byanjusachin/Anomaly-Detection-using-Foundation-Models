#!/bin/bash

#Configutation
RESOURCE_GROUP="anomaly_detection"

#Get the name of the storage account containing "cloudshellstorage"
STORAGE_ACCOUNT=$(az storage account list \
--resource-group $RESOURCE_GROUP \
--query "[?contains(name, 'llamamlws6782360884')].name" \ 
--output tsv)


# Fetch and export the connection string 
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
--name $STORAGE_ACCOUNT \
--resource-group $RESOURCE_GROUP \
--output tsv)

# Export the connection string to the current shell session
export AZURE_STORAGE_CONNECTION_STRING

echo "AZURE_STORAGE_CONNECTION_STRING set for storage account: $STORAGE_ACCOUNT"