import argparse
import os
import subprocess
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, Input, Output, command
from azure.ai.ml.entities import Data, Environment,Model
from azure.ai.ml.constants import AssetTypes
from utils import ensure_compute_exists
from azure.keyvault.secrets import SecretClient

load_dotenv()

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    resource_group_name=os.getenv("AZURE_RESOURCE_GROUP"),
    workspace_name=os.getenv("AZURE_WORKSPACE_NAME")
)
credential=DefaultAzureCredential()
key_vault_name = os.getenv("AZURE_KEY_VAULT_NAME")
key_vault_url = f"https://{key_vault_name}.vault.azure.net"

secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
hf_token = secret_client.get_secret("HF-TOKEN").value

EXPERIMENT_NAME = "llama-zero-shot-experiment"

COMPUTE_NAME = "llama-compute-zero"

env = Environment(
    name="llama-env-local",
    description="Environment using local conda file",
    conda_file="azure/ml/environment.yml",
    image="mcr.microsoft.com/azureml/base:openmpi3.1.2-ubuntu18.04",  # lightweight CPU base image
)

env.environment_variables = {
            "HF_TOKEN": hf_token #line makes it available inside the container
        }

def upload_to_blob(file_path):
    print(f" Uploading {file_path} to Azure Blob.")
    base_name = os.path.basename(file_path)
    data_name = os.path.splitext(base_name)[0]
    
    try:
        data_asset = Data(
            path=file_path,
            type=AssetTypes.URI_FILE,
            description="Uploaded input data",
            name=data_name,
            version="1",
        )
        registered_data = ml_client.data.create_or_update(data_asset)
        print(f" Uploaded to Blob: {registered_data.path}")
        return Input(type=AssetTypes.URI_FILE, path=registered_data.id)
    except Exception as e:
        print(" Dataset already exists, reusing it.")
        return Input(path=f"azureml:{data_name}:1", type=AssetTypes.URI_FILE)

def submit_job(input_data_path):
    print(" Submitting job to Azure ML...")
     
   

    job = command(
        code="./llama",  # path where zero_shot.py is located
        command="python zero_shot.py --input_data ${{inputs.input_data}}",
        inputs= { 
            "input_data": input_data_path
        },
        environment=env,
        compute=COMPUTE_NAME,
        instance_count=1,
        experiment_name=EXPERIMENT_NAME,
        description="Zero-shot inference with LLaMA 3.2 11B on uploaded blob dataset",
        environment_variables={
            "HF_TOKEN": hf_token
        }
        
    )

    return job


def run_pipeline(input_file):
    print("Ensuring compute cluster is ready...")
    ensure_compute_exists(COMPUTE_NAME)

    input_data_path = upload_to_blob(input_file)
    print(f" DEBUG: input_data_path = {input_data_path}")


    job = submit_job(input_data_path)
    returned_job = ml_client.jobs.create_or_update(job)
    print(f" Job submitted! Run ID: {returned_job.name}")
    print(f" Web view: {returned_job.studio_url}")
    ml_client.jobs.stream(returned_job.name)
  
    """zero_shot_job = submit_job(
        script_path="llama/zero_shot.py",
        job_name="zero-shot-detection",
        input_data_path=input_data_path,
        output_path="azureml://datastores/workspaceblobstore/paths/outputs/zero_shot_predictions.csv"
    )

    evaluate_job = submit_job(
        script_path="evaluation/evaluate.py",
        job_name="evaluate-zero-shot",
        input_data_path="azureml://datastores/workspaceblobstore/paths/outputs/zero_shot_predictions.csv",
        output_path="azureml://datastores/workspaceblobstore/paths/outputs/eval_results.json"
    )

    print(f"Jobs completed:\n  • Zero-shot: {zero_shot_job}\n  • Evaluation: {evaluate_job}")"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full AzureML pipeline for anomaly detection.")
    parser.add_argument("--input_file", required=True, help="Path to input file for detection")
    args = parser.parse_args()
    run_pipeline(args.input_file)
