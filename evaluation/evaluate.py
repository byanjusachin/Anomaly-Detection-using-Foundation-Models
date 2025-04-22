import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
import os
import json
from pathlib import Path

# Load from Azure ML inputs/outputs
INPUT_FILE = os.getenv("input_file", "outputs/zero_shot_predictions.csv")
OUTPUT_FILE = os.getenv("output_file", "outputs/eval_results.json")


def evaluate_results(input_file: str = INPUT_FILE, report_file: str = OUTPUT_FILE):
    print("Evaluating results from : {input_file}")

    df = pd.read_csv(input_file)

    if "ground_truth" not in df.columns or "prediction" not in df.columns:
        raise ValueError("CSV must contain 'ground_truth' and 'prediction' columns.")
    
    y_true = df['ground_truth']
    y_pred = df['prediction']

    try:
        auroc = roc_auc_score(y_true,y_pred)
    except ValueError:
        auroc = 0.0
        print("AUROC could not be computed")


    try:
        auprc =  average_precision_score(y_true, y_pred)
    except ValueError:
        auprc= 0.0
        print("AUPRC could not be computed")

    print(f"AUROC: {auroc:.4f}")
    print(f"AUPRC: {auprc:.4f}")

    # Saving evaluation results

    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w") as f:
        json.dump({"AUROC": auroc, "AUPRC": auprc}, f, indent=2)

    return auroc, auprc

if __name__ == "__main__":
    evaluate_results()


