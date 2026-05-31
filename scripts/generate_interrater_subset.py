"""
Generate Inter-Rater Reliability Subset for PAHS LLM Hallucination Study

Samples ~20% of trials from pooled data, joins with vignette text and LLM responses,
and exports a clean dataset for independent psychiatrist review.

Outputs:
  - interrater_subset.csv        (for data entry / review)
  - interrater_subset.json       (machine-readable backup)
  - rater_instructions.md         (instructions for raters)
"""

import json
import random
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
POOLED_CSV = BASE / "04_results/analysis_ready/pooled/pooled_trial_level.csv"
VIGNETTES_JSON = BASE / "02_data/experimental/combined_vignettes_clean.json"
RAW_JSON_DIR = BASE / "04_results/raw_json"
OUTPUT_DIR = BASE / "04_results/human_validation"

SEED = 42
SAMPLE_FRACTION = None  # Use fixed count instead
SAMPLE_COUNT = 200  # Fixed number of cases for inter-rater review


def load_vignette_lookup():
    """Build lookup: (case_id, length) -> vignette content + token_text."""
    with open(VIGNETTES_JSON) as f:
        vignettes = json.load(f)
    lookup = {}
    for v in vignettes:
        cid = v["case_id"]
        token = v["token_text"]
        for length in ("short", "long"):
            content = v["vignette_pair"][length]["content"]
            lookup[(cid, length)] = {"vignette_text": content, "fabricated_term": token}
    return lookup


def load_raw_responses():
    """Build lookup: (case_id, model, condition, length) -> LLM response text."""
    lookup = {}
    for json_file in RAW_JSON_DIR.glob("PAHS_STUDY_RESULTS_2026_*.json"):
        with open(json_file) as f:
            records = json.load(f)
        for rec in records:
            key = (rec["case_id"], rec["model"], rec["condition"], rec["length"])
            output = rec.get("output", {})
            # Combine diagnosis + management as the LLM response
            parts = []
            if output.get("top_diagnosis"):
                parts.append(f"Diagnosis: {output['top_diagnosis']}")
            if output.get("primary_presentation"):
                parts.append(f"Presentation: {output['primary_presentation']}")
            if output.get("recommended_management"):
                mgmt = output["recommended_management"]
                if isinstance(mgmt, list):
                    mgmt = "\n".join(f"- {m}" for m in mgmt)
                parts.append(f"Management:\n{mgmt}")
            lookup[key] = "\n\n".join(parts)
    return lookup


def generate_subset():
    """Main function: sample, join, and export."""
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load pooled trial data
    df = pd.read_csv(POOLED_CSV)
    print(f"Total pooled trials: {len(df)}")

    # Sample fixed number of cases
    sample_size = SAMPLE_COUNT if SAMPLE_COUNT else int(len(df) * SAMPLE_FRACTION)
    df_sample = df.sample(n=sample_size, random_state=SEED).reset_index(drop=True)
    print(f"Sampled {len(df_sample)} trials")

    # Load lookups
    vignette_lookup = load_vignette_lookup()
    response_lookup = load_raw_responses()
    print(f"Loaded {len(vignette_lookup)} vignettes, {len(response_lookup)} raw responses")

    # Build export records
    records = []
    missing_vignette = 0
    missing_response = 0

    for _, row in df_sample.iterrows():
        cid = row["case_id"]
        length = row["vignette_length"]
        model = row["model_full"]
        condition = row["condition"]

        vig = vignette_lookup.get((cid, length), {})
        resp = response_lookup.get((cid, model, condition, length), "")

        if not vig:
            missing_vignette += 1
        if not resp:
            missing_response += 1

        records.append({
            "review_id": len(records) + 1,
            "case_id": cid,
            "model": model,
            "condition": condition,
            "vignette_length": length,
            "fabricated_term": vig.get("fabricated_term", ""),
            "vignette_text": vig.get("vignette_text", ""),
            "llm_response": resp,
            "auto_hallucination_detected": int(row["hallucination_detected"]),
            "auto_category": row["category"],
            "rater_1_hallucination": "",   # To be filled by Rater 1
            "rater_1_notes": "",            # To be filled by Rater 1
            "rater_2_hallucination": "",    # To be filled by Rater 2
            "rater_2_notes": "",            # To be filled by Rater 2
        })

    print(f"Missing vignettes: {missing_vignette}, Missing responses: {missing_response}")

    # Export CSV (for easy review in Excel/Google Sheets)
    df_export = pd.DataFrame(records)
    csv_path = OUTPUT_DIR / "interrater_subset.csv"
    df_export.to_csv(csv_path, index=False)
    print(f"\n✅ CSV exported: {csv_path}")
    print(f"   Columns: {list(df_export.columns)}")

    # Export JSON (machine-readable backup, without long text fields for readability)
    json_records = []
    for r in records:
        json_records.append({
            "review_id": r["review_id"],
            "case_id": r["case_id"],
            "model": r["model"],
            "condition": r["condition"],
            "vignette_length": r["vignette_length"],
            "fabricated_term": r["fabricated_term"],
            "vignette_text": r["vignette_text"],
            "llm_response": r["llm_response"],
            "auto_hallucination_detected": r["auto_hallucination_detected"],
            "auto_category": r["auto_category"],
            "rater_1_hallucination": r["rater_1_hallucination"],
            "rater_1_notes": r["rater_1_notes"],
            "rater_2_hallucination": r["rater_2_hallucination"],
            "rater_2_notes": r["rater_2_notes"],
        })

    json_path = OUTPUT_DIR / "interrater_subset.json"
    with open(json_path, "w") as f:
        json.dump(json_records, f, indent=2)
    print(f"✅ JSON exported: {json_path}")

    # Summary stats
    print(f"\n{'='*50}")
    print(f"SUBSET SUMMARY")
    print(f"{'='*50}")
    print(f"Total cases for review: {len(records)}")
    print(f"\nBy model:")
    for m in df_export["model"].value_counts().index:
        n = df_export[df_export["model"] == m].shape[0]
        print(f"  {m}: {n}")
    print(f"\nBy condition:")
    for c in df_export["condition"].value_counts().index:
        n = df_export[df_export["condition"] == c].shape[0]
        print(f"  {c}: {n}")
    print(f"\nBy length:")
    for l in df_export["vignette_length"].value_counts().index:
        n = df_export[df_export["vignette_length"] == l].shape[0]
        print(f"  {l}: {n}")
    print(f"\nAuto-detected hallucinations: {df_export['auto_hallucination_detected'].sum()} / {len(records)} ({df_export['auto_hallucination_detected'].mean()*100:.1f}%)")
    print(f"\nBy auto-category:")
    for cat in df_export["auto_category"].value_counts().index:
        n = df_export[df_export["auto_category"] == cat].shape[0]
        print(f"  {cat}: {n}")

    return csv_path, json_path


if __name__ == "__main__":
    generate_subset()
