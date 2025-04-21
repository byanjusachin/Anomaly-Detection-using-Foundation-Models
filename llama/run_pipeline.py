from utils import ensure_compute_exists
from evaluation.evaluate import evaluate_results

#===CONFIGURATION ===
ZERO_SHOT_COMPUTE = "llama-compute-zero"
FEW_SHOT_COMPUTE = "llama-compute-fewshot"
AUGMENT_COMPUTE = "llama-compute-augment"


ZERO_SHOT_THRESHOLD = {"auroc": 0.8, "auprc": 0.7}
FEW_SHOT_THRESHOLD = {"auroc":0.85,"auprc":0.8}


def run_zero_shot():
    print("Running zero-shot detection...")

    pass

def run_few_shot():
    print("Running zero-shot detection ...")


    pass

def run_data_augmentation():
    print("Generating synthetic data ... ")


    pass

def main():

    # Call to compute target for zero-shot from utils
    ensure_compute_exists(ZERO_SHOT_COMPUTE)

    #Running zero-shot detection
    run_zero_shot()

    #Evaluating zero-shot results
    print("Evaluating zero-shot results...")
    zero_auroc, zero_auprc = evaluate_results("zero_shot")

    

