from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
import sys

#Storage Account and container details to upload files into into
storage_account_url ="https://llamamlws6782360884.blob.core.windows.net"
container_name ="azureml-blobstore-b7c414df-3828-467b-bfef-f764143fac7b"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


#Taking the file path from the from CLI
file_path = sys.argv[1] if len(sys.argv) > 1  else "data/test.csv"

#Extract just the filename
blob_base_name = os.path.basename(file_path)


def generate_unique_blob_name(blob_service_client, containter_name, base_name):
    name, ext = os.path.splitext(base_name)
    version = 1
    candidate_name = f"{name}_v{version}{ext}"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob = candidate_name)

    #Increment until we find a non-existing name
    while blob_client.exists():
        version += 1
        candidate_name =f"{name}_v{version}{ext}"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=candidate_name)
    
    return candidate_name

def upload():
    #Verify the local file exists
    if not os.path.exists(file_path):
        print(f"File not found:{file_path}")
        return

#Connection to the Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

#Generate a versioned blob name to avoid overwriting
final_blob_name = generate_unique_blob_name(blob_service_client,container_name, blob_base_name)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=final_blob_name)

#Upload the file
with open(file_path, "rb") as data:
    blob_client.upload_blob(data)

blob_url = f"{storage_account_url}/{container_name}/{final_blob_name}"
print(blob_url)


if __name__ == "__main__":
    upload()