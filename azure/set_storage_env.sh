#!/bin/bash

#Configutation
RESOURCE_GROUP="anomaly_detection"
STORAGE_ACCOUNT=$(az storage account list \
--resource-group $RESOURCE_GROUP \
--query "[?contains(name, 'cloudshellstorage')].name" \ 
--output tsv)


# Fetch and export the connection string 
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
--name $STORAGE_ACCOUNT \
--resource-group $RESOURCE_GROUP \
--output tsv)

echo "AZURE_STORAGE_CONNECTION_STRING set for storage account: $STORAGE_ACCOUNT"