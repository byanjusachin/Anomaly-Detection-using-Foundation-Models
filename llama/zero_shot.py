# llama/zero_shot.py

import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json
from pathlib import Path
import subprocess
from transformers import logging
from transformers import AutoConfig
from dotenv import load_dotenv

load_dotenv()




# Silence warning logs
logging.set_verbosity_error()


#Using azureMl enviornment for model pathe
MODEL_NAME="meta-llama/Llama-3.2-1B"
#HF_TOKEN = os.getenv("HF_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")


# Load input/output paths from env vars (Azure ML friendly)
INPUT_FILE = os.getenv("INPUT_DATA", "data/test.csv")
OUTPUT_FILE = os.getenv("OUTPUT_DATA", "outputs/zero_shot_predictions.csv")


PROMPT_TEMPLATE = """
You are an anomaly detection assistant.
Decide if the following is anomalous.
Is the following transaction anomalous? Answer with 1 for Yes or 0 for No.

Input: {}
Answer:
"""

def load_model():

    config = AutoConfig.from_pretrained(MODEL_NAME, use_auth_token=HF_TOKEN)
    if hasattr(config, "rope_scaling") and isinstance(config.rope_scaling, dict):
    # Override to only keep type and factor to prevent LLaMA error
        config.rope_scaling = {"type": "linear", "factor": 1.0}

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_auth_token=HF_TOKEN
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        use_auth_token=HF_TOKEN
    )
    return tokenizer, model

def run_inference(text, pipe):
    prompt = PROMPT_TEMPLATE.format(text)
    try:
        output = pipe(prompt, max_new_tokens=5, return_full_text=False)[0]["generated_text"]
        answer = output.strip().split()[0]
        return int(answer) if answer in ['0', '1'] else 0
    except Exception as e:
        print(f"Error during inference: {e}")
        return 0

def run_zero_shot():
    df = pd.read_csv(INPUT_FILE)
    if 'text' not in df.columns:
        df.rename(columns={df.columns[0]: 'text'}, inplace=True)
    if 'ground_truth' not in df.columns:
        df['ground_truth'] = 0

    tokenizer, model = load_model()
    
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)

    predictions = []
    

    for i, row in df.iterrows():
        pred = run_inference(row['text'], pipe)
        predictions.append(pred)
       
        print(f"[{i}] Predicted: {pred}")

    df['prediction'] = predictions
   

    Path(os.path.dirname(OUTPUT_FILE)).mkdir(parents=True, exist_ok=True)
    df[['ground_truth', 'prediction']].to_csv(OUTPUT_FILE, index=False)
    print(f" Saved predictions to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_zero_shot()
