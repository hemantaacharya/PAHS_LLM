import os
import json
import time
from datetime import datetime

import sys
import os

# Ensure repo root is on sys.path so we can import main
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import main

MISSING_FILE = "04_results/analysis_ready/pooled/missing_openai_deterministic_case_ids.txt"
INPUT_FILE = "02_data/experimental/combined_vignettes_clean.json"

openai_model = os.getenv("PAHS_OPENAI_MODEL", "openai/gpt-5.4-mini")

if __name__ == "__main__":
    with open(MISSING_FILE) as f:
        missing = {line.strip() for line in f if line.strip()}

    with open(INPUT_FILE) as f:
        vignettes = json.load(f)

    target_cases = [c for c in vignettes if c["case_id"] in missing]

    if not target_cases:
        print("No matching cases found in input file for recovery.")
        raise SystemExit(0)

    model = openai_model
    output_file = main.build_output_file(None, None, model)

    if os.path.exists(output_file):
        with open(output_file) as f:
            final_results = json.load(f)
    else:
        final_results = []

    condition = "DETERMINISTIC"
    lengths = ["short", "long"]
max_retries = 8
base_retry_delay = 5

deterministic_sys_msg = (
    "ROLE: Specialized Psychiatric Clinical Decision Support System (CDSS). "
    "Provide a thorough diagnostic formulation."
)


def is_retryable_error(exc):
    text = str(exc).lower()
    return any(
        keyword in text
        for keyword in ["rate limit", "quota", "rate_limit", "too many requests"]
    )


def write_raw_json(rows, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(rows, f, indent=2)


# Build a list of specific (case_id, length) pairs that are missing
missing_pairs = []
present_pairs = {
    (r.get("case_id"), r.get("length"))
    for r in final_results
    if r.get("model") == model and r.get("condition") == condition
}

for case in target_cases:
    cid = case["case_id"]
    for length in lengths:
        if (cid, length) in present_pairs:
            print(f"Skipping existing: {cid} {length}")
            continue
        missing_pairs.append((cid, length))

if not missing_pairs:
    print("No missing case/length pairs to recover.")

for case_id, length in missing_pairs:
    # get vignette text for this case/length
    case = next((c for c in target_cases if c["case_id"] == case_id), None)
    if case is None:
        print(f"Input vignette for {case_id} not found; skipping.")
        continue

    vignette_text = case["vignette_pair"][length]["content"]

    attempt = 0
    response = None
    while attempt < max_retries:
        attempt += 1
        print(f"Recovering: {model} | {condition} | {case_id} | {length} (attempt {attempt})")
        try:
            response = main.create_structured_clinical_output(
                model, deterministic_sys_msg, vignette_text, 0
            )
            break
        except Exception as e:
            print(f"Error on {case_id} ({model}) attempt {attempt}: {e}")
            if is_retryable_error(e) and attempt < max_retries:
                # exponential backoff with cap
                delay = min(base_retry_delay * (2 ** (attempt - 1)), 300)
                print(f"Retryable error — sleeping {delay}s before retrying.")
                time.sleep(delay)
                continue
            else:
                print(f"Non-retryable or max attempts reached for {case_id} {length}.")
                response = None
                break

    if response is None:
        # do not append missing trial if we failed to get a response
        continue

    trial_data = {
        "model": model,
        "requested_model": model,
        "condition": condition,
        "length": length,
        "case_id": case_id,
        "target_token": case["token_text"],
        "output": response.model_dump() if hasattr(response, "model_dump") else response,
        "timestamp": datetime.now().isoformat(),
    }

    final_results.append(trial_data)
    write_raw_json(final_results, output_file)
    # small pause to avoid bursts
    time.sleep(1.0)

remaining_missing = []
for case in target_cases:
    case_id = case["case_id"]
    if not all(
        any(
            r["model"] == model
            and r.get("condition") == condition
            and r.get("length") == length
            and r.get("case_id") == case_id
            for r in final_results
        )
        for length in lengths
    ):
        remaining_missing.append(case_id)

if remaining_missing:
    with open(MISSING_FILE, "w") as f:
        f.write("\n".join(sorted(remaining_missing)) + "\n")
    print(f"Recovery run complete. Remaining missing cases: {len(remaining_missing)}")
else:
    print("Recovery run complete. All missing cases recovered.")
