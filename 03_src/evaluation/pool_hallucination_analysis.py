import argparse
import csv
import glob
import json
import math
import os
from collections import defaultdict

from extract_hallucination_data import extract_hallucination_records


DEFAULT_INPUT_GLOB = "04_results/raw_json/*.json"
DEFAULT_OUTPUT_DIR = "04_results/analysis_ready/pooled"
CONDITIONS = ["DEFAULT", "SAFETY_INSTRUCTION", "DETERMINISTIC"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pool multi-provider PAHS outputs into standardized analysis tables."
    )
    parser.add_argument(
        "--input-glob",
        default=DEFAULT_INPUT_GLOB,
        help="Glob for raw result JSON files to include.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for pooled output tables.",
    )
    parser.add_argument(
        "--real-terms",
        nargs="*",
        default=["CIWA-Ar"],
        help="Known real terms used to avoid false-positive trap labeling.",
    )
    return parser.parse_args()


def to_bool(value):
    return 1 if bool(value) else 0


def safe_div(num, den):
    if not den:
        return 0.0
    return num / den


def parse_provider_model(model_str):
    if not model_str:
        return "unknown", "unknown"
    if "/" not in model_str:
        return "unknown", model_str
    provider, model = model_str.split("/", 1)
    return provider, model


def wilson_ci(successes, total, z=1.96):
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denom = 1 + (z ** 2) / total
    center = (p + (z ** 2) / (2 * total)) / denom
    margin = (
        z
        * math.sqrt((p * (1 - p) / total) + ((z ** 2) / (4 * (total ** 2))))
        / denom
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def rd_ci(p1, n1, p0, n0, z=1.96):
    if n1 == 0 or n0 == 0:
        return 0.0, 0.0
    rd = p1 - p0
    se = math.sqrt((p1 * (1 - p1) / n1) + (p0 * (1 - p0) / n0))
    return rd - z * se, rd + z * se


def rr_ci(a, n1, c, n0, z=1.96):
    # Haldane-Anscombe correction for zeros.
    a2 = a + 0.5
    c2 = c + 0.5
    n1_2 = n1 + 1.0
    n0_2 = n0 + 1.0

    p1 = a2 / n1_2
    p0 = c2 / n0_2
    rr = p1 / p0 if p0 else 0.0

    if a2 == 0 or c2 == 0:
        return rr, 0.0, 0.0

    se_log = math.sqrt((1 / a2) - (1 / n1_2) + (1 / c2) - (1 / n0_2))
    low = math.exp(math.log(rr) - z * se_log)
    high = math.exp(math.log(rr) + z * se_log)
    return rr, low, high


def write_csv(path, rows, columns):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_trials(input_glob, real_terms):
    pooled = []
    files = sorted(glob.glob(input_glob))

    for file_path in files:
        if not file_path.lower().endswith(".json"):
            continue

        with open(file_path, "r") as f:
            records = json.load(f)

        extracted = extract_hallucination_records(records, real_terms)
        for item in extracted:
            metadata = item.get("trial_metadata", {})
            output = item.get("output", {})
            logic = item.get("boolean_logic", {})

            model_full = metadata.get("model") or "unknown"
            provider, model_name = parse_provider_model(model_full)

            pooled.append(
                {
                    "provider": provider,
                    "model_name": model_name,
                    "model_full": model_full,
                    "condition": metadata.get("condition") or "UNKNOWN",
                    "vignette_length": metadata.get("vignette_length") or "UNKNOWN",
                    "case_id": metadata.get("case_id") or "UNKNOWN",
                    "hallucination_detected": to_bool(
                        output.get("hallucination_detected")
                    ),
                    "endorsed_hallucination": to_bool(
                        output.get("endorsed_hallucination")
                    ),
                    "adoption_rate_failure": to_bool(
                        logic.get("adoption_rate_failure")
                    ),
                    "detection_rate_success": to_bool(
                        logic.get("detection_rate_success")
                    ),
                    "dangerous_reasoning_hallucination": to_bool(
                        logic.get("dangerous_reasoning_hallucination")
                    ),
                    "category": item.get("analysis", {}).get("category", "UNKNOWN"),
                    "source_file": os.path.basename(file_path),
                }
            )

    return pooled, files


def aggregate_tables(trials):
    grouped_model = defaultdict(list)
    grouped_model_condition = defaultdict(list)
    grouped_model_condition_length = defaultdict(list)

    for row in trials:
        key_model = (row["provider"], row["model_name"])
        key_model_condition = (row["provider"], row["model_name"], row["condition"])
        key_mcl = (
            row["provider"],
            row["model_name"],
            row["condition"],
            row["vignette_length"],
        )
        grouped_model[key_model].append(row)
        grouped_model_condition[key_model_condition].append(row)
        grouped_model_condition_length[key_mcl].append(row)

    table1 = []
    for (provider, model_name), rows in sorted(grouped_model.items()):
        cond_counts = {c: 0 for c in CONDITIONS}
        length_counts = defaultdict(int)
        for r in rows:
            if r["condition"] in cond_counts:
                cond_counts[r["condition"]] += 1
            length_counts[r["vignette_length"]] += 1

        table1.append(
            {
                "provider": provider,
                "model_name": model_name,
                "completed_trials": len(rows),
                "default_n": cond_counts["DEFAULT"],
                "safety_instruction_n": cond_counts["SAFETY_INSTRUCTION"],
                "deterministic_n": cond_counts["DETERMINISTIC"],
                "short_n": length_counts.get("short", 0),
                "long_n": length_counts.get("long", 0),
            }
        )

    table2 = []
    for (provider, model_name, condition), rows in sorted(grouped_model_condition.items()):
        n = len(rows)
        hall = sum(r["hallucination_detected"] for r in rows)
        hall_rate = safe_div(hall, n)
        ci_low, ci_high = wilson_ci(hall, n)

        endorsed = sum(r["endorsed_hallucination"] for r in rows)
        endorsed_rate = safe_div(endorsed, n)

        table2.append(
            {
                "provider": provider,
                "model_name": model_name,
                "condition": condition,
                "n": n,
                "hallucination_count": hall,
                "hallucination_rate": round(hall_rate, 6),
                "hallucination_rate_pct": round(hall_rate * 100, 2),
                "endorsed_hallucination_count": endorsed,
                "endorsed_hallucination_rate": round(endorsed_rate, 6),
                "endorsed_hallucination_rate_pct": round(endorsed_rate * 100, 2),
                "hall_ci_low_pct": round(ci_low * 100, 2),
                "hall_ci_high_pct": round(ci_high * 100, 2),
                "adoption_failure_rate_pct": round(
                    safe_div(sum(r["adoption_rate_failure"] for r in rows), n) * 100,
                    2,
                ),
                "detection_success_rate_pct": round(
                    safe_div(sum(r["detection_rate_success"] for r in rows), n) * 100,
                    2,
                ),
                "dangerous_reasoning_rate_pct": round(
                    safe_div(
                        sum(r["dangerous_reasoning_hallucination"] for r in rows), n
                    )
                    * 100,
                    2,
                ),
            }
        )

    table3 = []
    for (provider, model_name), rows in sorted(grouped_model.items()):
        cond_map = defaultdict(list)
        for r in rows:
            cond_map[r["condition"]].append(r)

        baseline = cond_map.get("DEFAULT", [])
        n0 = len(baseline)
        c = sum(r["hallucination_detected"] for r in baseline)
        p0 = safe_div(c, n0)

        for comparison in ["SAFETY_INSTRUCTION", "DETERMINISTIC"]:
            target = cond_map.get(comparison, [])
            n1 = len(target)
            a = sum(r["hallucination_detected"] for r in target)
            p1 = safe_div(a, n1)

            rd = p1 - p0
            rd_low, rd_high = rd_ci(p1, n1, p0, n0)
            rr, rr_low, rr_high = rr_ci(a, n1, c, n0) if n1 and n0 else (0.0, 0.0, 0.0)

            table3.append(
                {
                    "provider": provider,
                    "model_name": model_name,
                    "comparison": f"{comparison}_vs_DEFAULT",
                    "default_n": n0,
                    "default_hallucinations": c,
                    "default_rate_pct": round(p0 * 100, 2),
                    "comparison_n": n1,
                    "comparison_hallucinations": a,
                    "comparison_rate_pct": round(p1 * 100, 2),
                    "risk_difference_pct": round(rd * 100, 2),
                    "rd_ci_low_pct": round(rd_low * 100, 2),
                    "rd_ci_high_pct": round(rd_high * 100, 2),
                    "risk_ratio": round(rr, 4),
                    "rr_ci_low": round(rr_low, 4),
                    "rr_ci_high": round(rr_high, 4),
                }
            )

    table4 = []
    for (provider, model_name, condition), rows in sorted(grouped_model_condition.items()):
        short_rows = [r for r in rows if r["vignette_length"] == "short"]
        long_rows = [r for r in rows if r["vignette_length"] == "long"]

        n_short = len(short_rows)
        n_long = len(long_rows)
        h_short = sum(r["hallucination_detected"] for r in short_rows)
        h_long = sum(r["hallucination_detected"] for r in long_rows)

        p_short = safe_div(h_short, n_short)
        p_long = safe_div(h_long, n_long)
        rd = p_short - p_long
        rd_low, rd_high = rd_ci(p_short, n_short, p_long, n_long)
        rr, rr_low, rr_high = (
            rr_ci(h_short, n_short, h_long, n_long)
            if n_short and n_long
            else (0.0, 0.0, 0.0)
        )

        table4.append(
            {
                "provider": provider,
                "model_name": model_name,
                "condition": condition,
                "short_n": n_short,
                "short_hallucinations": h_short,
                "short_rate_pct": round(p_short * 100, 2),
                "long_n": n_long,
                "long_hallucinations": h_long,
                "long_rate_pct": round(p_long * 100, 2),
                "risk_difference_pct": round(rd * 100, 2),
                "rd_ci_low_pct": round(rd_low * 100, 2),
                "rd_ci_high_pct": round(rd_high * 100, 2),
                "risk_ratio": round(rr, 4),
                "rr_ci_low": round(rr_low, 4),
                "rr_ci_high": round(rr_high, 4),
            }
        )

    return table1, table2, table3, table4


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    trials, source_files = load_trials(args.input_glob, args.real_terms)
    if not trials:
        raise ValueError(
            f"No trials found. Check --input-glob path: {args.input_glob}"
        )

    table1, table2, table3, table4 = aggregate_tables(trials)

    pooled_path = os.path.join(args.output_dir, "pooled_trial_level.csv")
    table1_path = os.path.join(args.output_dir, "table1_coverage.csv")
    table2_path = os.path.join(args.output_dir, "table2_outcomes_by_model_condition.csv")
    table3_path = os.path.join(args.output_dir, "table3_condition_effects.csv")
    table4_path = os.path.join(args.output_dir, "table4_length_effects.csv")
    summary_path = os.path.join(args.output_dir, "run_summary.json")

    pooled_columns = [
        "provider",
        "model_name",
        "model_full",
        "condition",
        "vignette_length",
        "case_id",
        "hallucination_detected",
        "endorsed_hallucination",
        "adoption_rate_failure",
        "detection_rate_success",
        "dangerous_reasoning_hallucination",
        "category",
        "source_file",
    ]
    write_csv(pooled_path, trials, pooled_columns)

    write_csv(
        table1_path,
        table1,
        [
            "provider",
            "model_name",
            "completed_trials",
            "default_n",
            "safety_instruction_n",
            "deterministic_n",
            "short_n",
            "long_n",
        ],
    )

    write_csv(
        table2_path,
        table2,
        [
            "provider",
            "model_name",
            "condition",
            "n",
            "hallucination_count",
            "hallucination_rate",
            "hallucination_rate_pct",
            "endorsed_hallucination_count",
            "endorsed_hallucination_rate",
            "endorsed_hallucination_rate_pct",
            "hall_ci_low_pct",
            "hall_ci_high_pct",
            "adoption_failure_rate_pct",
            "detection_success_rate_pct",
            "dangerous_reasoning_rate_pct",
        ],
    )

    write_csv(
        table3_path,
        table3,
        [
            "provider",
            "model_name",
            "comparison",
            "default_n",
            "default_hallucinations",
            "default_rate_pct",
            "comparison_n",
            "comparison_hallucinations",
            "comparison_rate_pct",
            "risk_difference_pct",
            "rd_ci_low_pct",
            "rd_ci_high_pct",
            "risk_ratio",
            "rr_ci_low",
            "rr_ci_high",
        ],
    )

    write_csv(
        table4_path,
        table4,
        [
            "provider",
            "model_name",
            "condition",
            "short_n",
            "short_hallucinations",
            "short_rate_pct",
            "long_n",
            "long_hallucinations",
            "long_rate_pct",
            "risk_difference_pct",
            "rd_ci_low_pct",
            "rd_ci_high_pct",
            "risk_ratio",
            "rr_ci_low",
            "rr_ci_high",
        ],
    )

    summary = {
        "input_glob": args.input_glob,
        "source_files_included": [os.path.basename(path) for path in source_files],
        "pooled_trials": len(trials),
        "unique_model_count": len(
            {(row["provider"], row["model_name"]) for row in trials}
        ),
        "output_files": [
            os.path.basename(pooled_path),
            os.path.basename(table1_path),
            os.path.basename(table2_path),
            os.path.basename(table3_path),
            os.path.basename(table4_path),
        ],
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Pooled trial-level file: {pooled_path}")
    print(f"Coverage table: {table1_path}")
    print(f"Outcomes table: {table2_path}")
    print(f"Condition effects table: {table3_path}")
    print(f"Length effects table: {table4_path}")
    print(f"Run summary: {summary_path}")
    print(f"Included source files: {len(source_files)}")
    print(f"Total pooled trials: {len(trials)}")


if __name__ == "__main__":
    main()
