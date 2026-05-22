import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def main():
    base = "04_results/analysis_ready/pooled"
    fig_dir = os.path.join(base, "figures")
    ensure_dir(fig_dir)

    path = os.path.join(base, "pooled_trial_level.csv")
    df = pd.read_csv(path)

    # Keep only the top 3 models
    top3 = ["anthropic/claude-haiku-4-5", "gemini/gemini-3.1-flash-lite", "openai/gpt-5.4-mini"]
    df = df[df["model_full"].isin(top3)].copy()

    # Ensure numeric columns
    for col in [
        "hallucination_detected",
        "endorsed_hallucination",
        "adoption_rate_failure",
        "detection_rate_success",
        "dangerous_reasoning_hallucination",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    agg = (
        df.groupby(["model_full", "condition", "vignette_length"], dropna=False)
        .agg(
            trials=("case_id", "count"),
            unique_cases=("case_id", lambda s: s.nunique()),
            hallucination_rate=("hallucination_detected", "mean"),
            endorsed_hallucination_rate=("endorsed_hallucination", "mean"),
            adoption_failure_rate=("adoption_rate_failure", "mean"),
            detection_success_rate=("detection_rate_success", "mean"),
            dangerous_rate=("dangerous_reasoning_hallucination", "mean"),
        )
        .reset_index()
    )

    for col in [
        "hallucination_rate",
        "endorsed_hallucination_rate",
        "adoption_failure_rate",
        "detection_success_rate",
        "dangerous_rate",
    ]:
        agg[col + "_pct"] = agg[col].apply(lambda x: x * 100 if x <= 1 else x)

    sns.set(style="whitegrid", font_scale=1.0)

    metrics = [
        ("endorsed_hallucination_rate_pct", "Endorsed hallucination rate (%)"),
        ("hallucination_rate_pct", "Hallucination-detected rate (%)"),
        ("adoption_failure_rate_pct", "Adoption-failure rate (%)"),
        ("detection_success_rate_pct", "Detection-success rate (%)"),
        ("dangerous_rate_pct", "Dangerous hallucination rate (%)"),
    ]

    for metric, title in metrics:
        g = sns.catplot(
            data=agg,
            x="condition",
            y=metric,
            hue="vignette_length",
            col="model_full",
            kind="bar",
            height=5,
            aspect=1.1,
            sharey=False,
            palette="muted",
            legend_out=True,
            margin_titles=True,
        )
        g.set_axis_labels("Condition", title)
        g.set_titles("{col_name}")
        for ax in g.axes.flatten():
            for label in ax.get_xticklabels():
                label.set_rotation(25)
                label.set_horizontalalignment("right")
            ax.set_xlabel("")
        g.fig.subplots_adjust(top=0.86, right=0.92)
        g.fig.suptitle(f"{title} for top 3 models, by condition and vignette length", fontsize=14)
        out = os.path.join(fig_dir, f"top3_{metric}.png")
        g.savefig(out, dpi=200)
        plt.close()

    print("WROTE top-3 visuals to", fig_dir)


if __name__ == "__main__":
    main()
