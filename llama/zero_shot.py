# llama/zero_shot.py

import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json
from pathlib import Path

# Load input/output paths from env vars (Azure ML friendly)
INPUT_FILE = os.getenv("INPUT_FILE", "data/test.csv")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "outputs/zero_shot_predictions.csv")

MODEL_NAME = "meta-llama/Meta-Llama-3-11B-Instruct"

PROMPT_TEMPLATE = """
You are an anomaly detection assistant.
Decide if the following is anomalous.
Respond in JSON: {{"prediction": 0 or 1, "reason": "short explanation"}}

Input: {}
"""

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model

def run_inference(text, pipe):
    prompt = PROMPT_TEMPLATE.format(text)
    output = pipe(prompt, max_new_tokens=256, return_full_text=False)[0]["generated_text"]
    try:
        json_part = output.split("{", 1)[1]
        parsed = json.loads("{" + json_part)
        return int(parsed.get("prediction", 0)), parsed.get("reason", "")
    except Exception:
        return 0, "Could not parse model output"

def run_zero_shot():
    df = pd.read_csv(INPUT_FILE)
    if 'text' not in df.columns:
        df.rename(columns={df.columns[0]: 'text'}, inplace=True)
    if 'ground_truth' not in df.columns:
        df['ground_truth'] = 0

    tokenizer, model = load_model()
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)

    predictions = []
    reasons = []

    for i, row in df.iterrows():
        pred, reason = run_inference(row['text'], pipe)
        predictions.append(pred)
        reasons.append(reason)
        print(f"[{i}] Predicted: {pred}, Reason: {reason[:50]}")

    df['prediction'] = predictions
    df['reason'] = reasons

    Path(os.path.dirname(OUTPUT_FILE)).mkdir(parents=True, exist_ok=True)
    df[['ground_truth', 'prediction', 'reason']].to_csv(OUTPUT_FILE, index=False)
    print(f" Saved predictions to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_zero_shot()
