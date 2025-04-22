import argparse
import os
import subprocess
from dotenv import load_dotenv
from azure.ai.ml import MLClient, Input, command
from llama.utils import ensure_compute_exists

load_dotenv()  # Load .env with AZURE_* values

# Azure ML workspace connection
ml_client =  MLClient.from_config()

COMPUTE_NAME = "llama-compute-zero"
ENV_YAML = "azure/ml/environment.yml"


def upload_to_blob(input_file: str) -> str:
    print(f"📤 Uploading {input_file} to Azure Blob...")
    result = subprocess.run(
        ["python", "azure/storage/upload_to_blob.py", "--file", input_file],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ Upload failed:", result.stderr)
        exit(1)

    blob_uri = result.stdout.strip()
    print(f"✅ Uploaded to Blob: {blob_uri}")
    return blob_uri


def submit_job(script_path, job_name, input_blob_uri, output_path):
    print(f"🚀 Submitting Azure ML job: {job_name}")

    job = command(
        code="./",  # Entire repo is code base
        command=f"python {script_path}",
        environment=f"./{ENV_YAML}",
        compute=COMPUTE_NAME,
        display_name=job_name,
        experiment_name="anomaly-detection",
        inputs={
            "INPUT_FILE": Input(type="uri_file", path=input_blob_uri)
        },
        outputs={
            "OUTPUT_FILE": output_path
        }
    )

    returned_job = ml_client.jobs.create_or_update(job)
    ml_client.jobs.stream(returned_job.name)  # Real-time logs
    return returned_job.name


def run_pipeline(input_file):
    print("🔁 Ensuring compute exists...")
    ensure_compute_exists(COMPUTE_NAME)

    blob_uri = upload_to_blob(input_file)

    # Step 1: Zero-Shot Detection
    zero_shot_job = submit_job(
        script_path="llama/zero_shot.py",
        job_name="zero-shot-detection",
        input_blob_uri=blob_uri,
        output_path="azureml://datastores/workspaceblobstore/paths/outputs/zero_shot_predictions.csv"
    )

    # Step 2: Evaluation
    evaluate_job = submit_job(
        script_path="evaluation/evaluate.py",
        job_name="evaluate-zero-shot",
        input_blob_uri="azureml://datastores/workspaceblobstore/paths/outputs/zero_shot_predictions.csv",
        output_path="azureml://datastores/workspaceblobstore/paths/outputs/eval_results.json"
    )

    print(f"✅ Jobs completed.\n📄 Zero-shot job: {zero_shot_job}\n📊 Evaluation job: {evaluate_job}")
    print("💡 Your compute will scale down after idle timeout (default: 2 mins).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full anomaly detection pipeline on Azure ML.")
    parser.add_argument("--input_file", required=True, help="Local path to the input data file")
    args = parser.parse_args()
    run_pipeline(args.input_file)
