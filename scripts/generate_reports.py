import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def main():
    base = "04_results/analysis_ready/pooled"
    fig_dir = os.path.join(base, "figures")
    ensure_dir(fig_dir)

    by_model = pd.read_csv(os.path.join(base, "comprehensive_by_model.csv"))
    by_model_cond = pd.read_csv(os.path.join(base, "comprehensive_by_model_condition.csv"))

    # Normalize rates to percent if they're in 0-1 range; detect by max value
    def to_pct(s):
        if s.max() <= 1.01:
            return s * 100
        return s

    by_model["hallucination_rate_pct"] = to_pct(by_model["hallucination_rate"]) if "hallucination_rate" in by_model.columns else 0
    by_model_cond["hallucination_rate_pct"] = to_pct(by_model_cond["hallucination_rate"]) if "hallucination_rate" in by_model_cond.columns else 0

    sns.set(style="whitegrid")

    # Bar: hallucination rate by model
    plt.figure(figsize=(8,5))
    ax = sns.barplot(data=by_model.sort_values("hallucination_rate_pct", ascending=False), x="hallucination_rate_pct", y="model", palette="viridis")
    ax.set_xlabel("Hallucination rate (%)")
    ax.set_ylabel("")
    plt.title("Hallucination rate by model")
    plt.tight_layout()
    p1 = os.path.join(fig_dir, "hallucination_rate_by_model.png")
    plt.savefig(p1, dpi=150)
    plt.close()

    # Clustered bar: by model and condition
    plt.figure(figsize=(10,6))
    pivot = by_model_cond.pivot(index='model', columns='condition', values='hallucination_rate')
    if pivot.isnull().values.any():
        pivot = pivot.fillna(0)
    pivot_pct = pivot.apply(lambda col: col * 100 if col.max() <= 1.01 else col)
    pivot_pct.plot(kind='bar', figsize=(10,6))
    plt.ylabel('Hallucination rate (%)')
    plt.title('Hallucination rate by model and condition')
    plt.tight_layout()
    p2 = os.path.join(fig_dir, "hallucination_rate_by_model_condition.png")
    plt.savefig(p2, dpi=150)
    plt.close()

    # Save an Excel workbook with sheets
    out_xlsx = os.path.join(base, "report_summary.xlsx")
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        by_model.to_excel(writer, sheet_name="by_model", index=False)
        by_model_cond.to_excel(writer, sheet_name="by_model_condition", index=False)
        # include the pivot as a sheet
        pivot_pct.reset_index().to_excel(writer, sheet_name="pivot_model_condition", index=False)

    print("WROTE", p1, p2, out_xlsx)

if __name__ == '__main__':
    main()
