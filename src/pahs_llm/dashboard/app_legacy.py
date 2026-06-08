"""
PAHS LLM Hallucination Study — Interactive Dashboard
Run: streamlit run dashboard.py
"""
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
TRIAL_CSV = "04_results/analysis_ready/pooled/pooled_trial_level.csv"
TABLE2_CSV = "04_results/analysis_ready/pooled/table2_outcomes_by_model_condition.csv"
TABLE3_CSV = "04_results/analysis_ready/pooled/table3_condition_effects.csv"
TABLE4_CSV = "04_results/analysis_ready/pooled/table4_length_effects.csv"
TABLE1_CSV = "04_results/analysis_ready/pooled/table1_coverage.csv"
RUN_SUMMARY = "04_results/analysis_ready/pooled/run_summary.json"
DASHBOARD_JSON = "04_results/analysis_ready/PAHS_STUDY_2026_DASHBOARD.json"
VIGNETTES_JSON = "02_data/experimental/combined_vignettes_clean.json"

CATEGORY_COLORS = {
    "Successful Defense": "#2ecc71",
    "Silent Adoption": "#f39c12",
    "Blind Spot": "#e74c3c",
    "False Positive": "#9b59b6",
}
CATEGORY_ORDER = [
    "Successful Defense",
    "Silent Adoption",
    "Blind Spot",
    "False Positive",
]
CATEGORY_NUM = {
    "Silent Adoption": 0,
    "False Positive": 1,
    "Blind Spot": 2,
    "Successful Defense": 3,
}
MODEL_COLORS = {
    "anthropic/claude-haiku-4-5": "#9b59b6",
    "gemini/gemini-3.1-flash-lite": "#3498db",
    "openai/gpt-5.4-mini": "#e67e22",
    "openrouter/meta-llama/llama-3.3-70b-instruct": "#1abc9c",
}
MODEL_LABELS = {
    "anthropic/claude-haiku-4-5": "Claude Haiku 4.5",
    "gemini/gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite",
    "openai/gpt-5.4-mini": "GPT-5.4-mini",
    "openrouter/meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
}
CONDITION_COLORS = {
    "DEFAULT": "#2ecc71",
    "DETERMINISTIC": "#3498db",
    "SAFETY_INSTRUCTION": "#e74c3c",
}
TOKEN_CATEGORY_LABELS = {
    "pathway_of_care": "Pathway of care",
    "laboratory_markers": "Laboratory markers",
    "pharmacological_agents": "Pharmacological agents",
    "assessment_diagnostic_criteria": "Assessment / diagnostic",
}

st.set_page_config(
    page_title="PAHS LLM Hallucination Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
)


def model_label(model_full):
    return MODEL_LABELS.get(model_full, model_full.split("/")[-1])


def add_model_label(df, col="model_full", out="model_label"):
    out_df = df.copy()
    out_df[out] = out_df[col].map(model_label)
    return out_df


def pct(value, digits=1):
    if pd.isna(value):
        return "—"
    return f"{100 * value:.{digits}f}%"


def category_rates(frame):
    counts = frame["category"].value_counts()
    total = len(frame) or 1
    return {cat: counts.get(cat, 0) / total for cat in CATEGORY_ORDER}


def paginate_dataframe(df, page_size=20):
    """Add pagination controls to a dataframe display."""
    if len(df) <= page_size:
        return df, 1, 1
    
    total_pages = (len(df) + page_size - 1) // page_size
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous", disabled=True):
            pass
    
    with col2:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("Next →", disabled=True):
            pass
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx], page, total_pages


def calculate_significance_indicator(ci_low, ci_high, null_value=1.0):
    """
    Determine if a confidence interval excludes the null value.
    Returns significance indicator and stars.
    """
    if ci_low is None or ci_high is None:
        return "", ""
    
    if ci_low > null_value or ci_high < null_value:
        return "✓", "***"
    else:
        return "", ""


def generate_summary_report(fdf, ft2, ft3, ft4):
    """Generate a summary report as markdown text."""
    report = []
    report.append("# PAHS LLM Hallucination Study - Summary Report")
    report.append(f"\n**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Trials:** {len(fdf):,}")
    report.append(f"**Models:** {fdf['model_full'].nunique()}")
    report.append(f"**Conditions:** {fdf['condition'].nunique()}")
    report.append(f"**Cases:** {fdf['case_id'].nunique()}")
    
    report.append("\n## Key Findings")
    
    # Overall rates
    report.append(f"\n### Overall Performance")
    report.append(f"- **Detection Success Rate:** {fdf['detection_rate_success'].mean()*100:.1f}%")
    report.append(f"- **Adoption Failure Rate:** {fdf['adoption_rate_failure'].mean()*100:.1f}%")
    report.append(f"- **Hallucination Detected:** {fdf['hallucination_detected'].mean()*100:.1f}%")
    report.append(f"- **Dangerous Reasoning:** {fdf['dangerous_reasoning_hallucination'].mean()*100:.2f}%")
    
    # Category distribution
    cat_rates = category_rates(fdf)
    report.append(f"\n### Outcome Categories")
    report.append(f"- **Successful Defense:** {cat_rates['Successful Defense']*100:.1f}%")
    report.append(f"- **Silent Adoption:** {cat_rates['Silent Adoption']*100:.1f}%")
    report.append(f"- **Blind Spot:** {cat_rates['Blind Spot']*100:.1f}%")
    report.append(f"- **False Positive:** {cat_rates['False Positive']*100:.1f}%")
    
    # Top performing model
    model_perf = fdf.groupby("model_full")["detection_rate_success"].mean().sort_values(ascending=False)
    top_model = model_perf.index[0]
    report.append(f"\n### Best Performing Model")
    report.append(f"- **{model_label(top_model)}:** {model_perf.iloc[0]*100:.1f}% detection success")
    
    report.append("\n---")
    report.append("\n*This report was generated automatically from the PAHS LLM Hallucination Study Dashboard.*")
    
    return "\n".join(report)


@st.cache_data
def load():
    with st.spinner("Loading data..."):
        df = pd.read_csv(TRIAL_CSV)
        t2 = pd.read_csv(TABLE2_CSV)
        t3 = pd.read_csv(TABLE3_CSV)
        t4 = pd.read_csv(TABLE4_CSV)
        t1 = pd.read_csv(TABLE1_CSV)

        for table in (t2, t3, t4, t1):
            table["model_full"] = table["provider"] + "/" + table["model_name"]

        if os.path.exists(VIGNETTES_JSON):
            with open(VIGNETTES_JSON) as f:
                vignettes = json.load(f)
            meta = pd.DataFrame(
                [
                    {
                        "case_id": row["case_id"],
                        "token_text": row["token_text"],
                        "token_category": row.get("category", "unknown"),
                    }
                    for row in vignettes
                ]
            )
            df = df.merge(meta, on="case_id", how="left")
        else:
            df["token_text"] = None
            df["token_category"] = "unknown"

        dashboard = None
        if os.path.exists(DASHBOARD_JSON):
            with open(DASHBOARD_JSON) as f:
                dashboard = json.load(f)

        run_summary = None
        if os.path.exists(RUN_SUMMARY):
            with open(RUN_SUMMARY) as f:
                run_summary = json.load(f)

    return df, t2, t3, t4, t1, dashboard, run_summary


def build_leaderboard(frame):
    rows = []
    grouped = frame.groupby(["model_full", "condition"], sort=False)
    for (model_full, condition), group in grouped:
        rates = category_rates(group)
        rows.append(
            {
                "model_full": model_full,
                "model_label": model_label(model_full),
                "condition": condition,
                "total_trials": len(group),
                "successful_defense_rate": rates["Successful Defense"],
                "silent_adoption_rate": rates["Silent Adoption"],
                "false_positive_rate": rates["False Positive"],
                "blind_spot_rate": rates["Blind Spot"],
                "dangerous_reasoning_hallucination_rate": group[
                    "dangerous_reasoning_hallucination"
                ].mean(),
            }
        )

    ranked = sorted(
        rows,
        key=lambda row: (
            -row["successful_defense_rate"],
            row["silent_adoption_rate"],
            row["dangerous_reasoning_hallucination_rate"],
            -row["total_trials"],
            row["model_full"],
            row["condition"],
        ),
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return pd.DataFrame(ranked)


df, t2, t3, t4, t1, dashboard_json, run_summary = load()

EXCLUDE = {"openai/gpt-5.5", "anthropic/claude-sonnet-4-6"}
df = df[~df["model_full"].isin(EXCLUDE)]
t2 = t2[~t2["model_full"].isin(EXCLUDE)]
t3 = t3[~t3["model_full"].isin(EXCLUDE)]
t4 = t4[~t4["model_full"].isin(EXCLUDE)]
t1 = t1[~t1["model_full"].isin(EXCLUDE)]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_models = sorted(df["model_full"].unique())
all_conditions = sorted(df["condition"].unique())
all_lengths = sorted(df["vignette_length"].unique())
all_token_categories = sorted(df["token_category"].dropna().unique())

# Initialize session state for drill-down
if "selected_model_from_chart" not in st.session_state:
    st.session_state.selected_model_from_chart = None

sel_models = st.sidebar.multiselect("Models", all_models, default=all_models, key="model_select")
sel_conditions = st.sidebar.multiselect("Conditions", all_conditions, default=all_conditions, key="condition_select")
sel_lengths = st.sidebar.multiselect("Vignette length", all_lengths, default=all_lengths, key="length_select")
sel_token_categories = st.sidebar.multiselect(
    "Fabricated token category",
    all_token_categories,
    default=all_token_categories,
    key="token_select"
)

# Reset filters button
if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.selected_model_from_chart = None
    st.rerun()

fdf = df[
    df["model_full"].isin(sel_models)
    & df["condition"].isin(sel_conditions)
    & df["vignette_length"].isin(sel_lengths)
    & df["token_category"].isin(sel_token_categories)
]
ft2 = t2[t2["model_full"].isin(sel_models) & t2["condition"].isin(sel_conditions)]
ft3 = t3[t3["model_full"].isin(sel_models)]
ft4 = t4[t4["model_full"].isin(sel_models) & t4["condition"].isin(sel_conditions)]
ft1 = t1[t1["model_full"].isin(sel_models)]

with st.sidebar.expander("Study design", expanded=False):
    n_cases = df["case_id"].nunique()
    n_models = len(all_models)
    st.markdown(
        f"""
        - **Site:** Patan Academy of Health Sciences
        - **Cases:** {n_cases} vignettes (short + long)
        - **Models:** 4 LLMs
        - **Conditions:** DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC
        - **Fabricated tokens:** planted clinical terms per case
        """
    )
    if run_summary:
        st.caption(
            f"Pooled from {run_summary.get('pooled_trials', '—'):,} trials · "
            f"{run_summary.get('unique_model_count', '—')} models"
        )

# ── Header ────────────────────────────────────────────────────────────────────
st.title("PAHS LLM Hallucination Study")
st.caption(
    f"Patan Academy of Health Sciences · 2026 · "
    f"{df['case_id'].nunique()} vignettes · {len(all_models)} models · "
    f"{len(all_conditions)} conditions · {len(df):,} pooled trials"
)

# Generate and offer summary report download
summary_report = generate_summary_report(fdf, ft2, ft3, ft4)
st.download_button(
    "📄 Download Summary Report",
    summary_report,
    "PAHS_Summary_Report.md",
    "text/markdown",
    key="summary_report_download"
)

with st.expander("What the outcome categories mean"):
    st.markdown(
        """
        | Category | What happened | Clinical risk |
        | --- | --- | --- |
        | **Successful Defense** | Fake term detected and excluded | None — goal behavior |
        | **Silent Adoption** | Fake term accepted as real | **High** — hallucination in reasoning |
        | **False Positive** | Real term wrongly flagged as fake | Moderate — alert fatigue |
        | **Blind Spot** | Fake term ignored, neither adopted nor flagged | Low–moderate — noise unnoticed |
        """
    )

# ── KPIs ──────────────────────────────────────────────────────────────────────
n = len(fdf)
cat_rates = category_rates(fdf) if n else {cat: 0 for cat in CATEGORY_ORDER}

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Trials", f"{n:,}")
    st.metric("Successful Defense", pct(cat_rates["Successful Defense"]))
with m2:
    st.metric("Detection success", pct(fdf["detection_rate_success"].mean()) if n else "—")
    st.metric("Silent Adoption", pct(cat_rates["Silent Adoption"]))
with m3:
    st.metric("Adoption failure", pct(fdf["adoption_rate_failure"].mean()) if n else "—")
    st.metric("Blind Spot", pct(cat_rates["Blind Spot"]))
with m4:
    st.metric("Hallucination flagged", pct(fdf["hallucination_detected"].mean()) if n else "—")
    st.metric("False Positive", pct(cat_rates["False Positive"]))
with m5:
    st.metric("Dangerous reasoning", pct(fdf["dangerous_reasoning_hallucination"].mean(), 2) if n else "—")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Overview",
    "Leaderboard",
    "Condition Effects",
    "Length Effects",
    "Token Analysis",
    "Case Explorer",
    "Publication Tables",
    "Help & Guide",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns(2)

    with left:
        st.subheader("Hallucination rate by model (95% CI)")
        agg = (
            ft2.groupby("model_full")
            .apply(
                lambda x: pd.Series(
                    {
                        "rate": x["hallucination_rate_pct"].mean(),
                        "ci_low": x["hall_ci_low_pct"].mean(),
                        "ci_high": x["hall_ci_high_pct"].mean(),
                    }
                ),
                include_groups=False,
            )
            .reset_index()
            .sort_values("rate")
        )
        agg["model_label"] = agg["model_full"].map(model_label)
        fig = go.Figure()
        for _, row in agg.iterrows():
            color = MODEL_COLORS.get(row["model_full"], "#888")
            fig.add_trace(
                go.Bar(
                    x=[row["rate"]],
                    y=[row["model_label"]],
                    orientation="h",
                    marker_color=color,
                    error_x=dict(
                        type="data",
                        symmetric=False,
                        array=[row["ci_high"] - row["rate"]],
                        arrayminus=[row["rate"] - row["ci_low"]],
                        color="#333",
                        thickness=2,
                    ),
                    text=f"{row['rate']:.1f}%",
                    textposition="outside",
                    showlegend=False,
                )
            )
        fig.update_layout(
            xaxis=dict(title="Hallucination rate (%)", range=[0, 105]),
            yaxis=dict(title=""),
            margin=dict(l=0, r=30, t=10, b=10),
            height=max(240, 70 * len(agg)),
        )
        st.plotly_chart(fig, width='stretch')

    with right:
        st.subheader("Outcome category distribution")
        cat = fdf["category"].value_counts().reset_index()
        cat.columns = ["category", "count"]
        fig2 = px.pie(
            cat,
            names="category",
            values="count",
            color="category",
            color_discrete_map=CATEGORY_COLORS,
            category_orders={"category": CATEGORY_ORDER},
            hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=280)
        st.plotly_chart(fig2, width='stretch')

    st.subheader("Outcome categories by model (stacked %)")
    cat_model = fdf.groupby(["model_full", "category"]).size().reset_index(name="count")
    cat_model["model_label"] = cat_model["model_full"].map(model_label)
    totals = cat_model.groupby("model_full")["count"].transform("sum")
    cat_model["pct"] = cat_model["count"] / totals * 100
    fig3 = px.bar(
        cat_model,
        x="model_label",
        y="pct",
        color="category",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"category": CATEGORY_ORDER},
        text=cat_model["pct"].map("{:.1f}%".format),
        labels={"model_label": "Model", "pct": "%", "category": "Outcome"},
    )
    fig3.update_traces(textposition="inside")
    fig3.update_layout(
        barmode="stack",
        yaxis_ticksuffix="%",
        margin=dict(l=0, r=0, t=10, b=10),
        height=340,
    )
    st.plotly_chart(fig3, width='stretch')

    radar_col, compare_col = st.columns(2)

    with radar_col:
        st.subheader("Model safety profile")
        st.caption("Higher is better on all axes")
        radar_rows = []
        for model_full, group in fdf.groupby("model_full"):
            rates = category_rates(group)
            radar_rows.append(
                {
                    "model_label": model_label(model_full),
                    "Defense": rates["Successful Defense"] * 100,
                    "Low adoption": (1 - rates["Silent Adoption"]) * 100,
                    "Detection": group["detection_rate_success"].mean() * 100,
                    "Low blind spot": (1 - rates["Blind Spot"]) * 100,
                }
            )
        radar_df = pd.DataFrame(radar_rows)
        if not radar_df.empty:
            metrics = ["Defense", "Low adoption", "Detection", "Low blind spot"]
            fig_radar = go.Figure()
            for _, row in radar_df.iterrows():
                values = [row[m] for m in metrics] + [row[metrics[0]]]
                fig_radar.add_trace(
                    go.Scatterpolar(
                        r=values,
                        theta=metrics + [metrics[0]],
                        fill="toself",
                        name=row["model_label"],
                        opacity=0.65,
                    )
                )
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
                margin=dict(l=40, r=40, t=30, b=10),
                height=360,
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig_radar, width='stretch')

    with compare_col:
        st.subheader("Detected vs endorsed hallucination")
        st.caption("Endorsed = model agreed with the fabricated detail")
        end_agg = (
            fdf.groupby("model_full")[["hallucination_detected", "endorsed_hallucination"]]
            .mean()
            .mul(100)
            .reset_index()
        )
        end_agg["model_label"] = end_agg["model_full"].map(model_label)
        end_long = end_agg.melt(
            id_vars=["model_full", "model_label"],
            var_name="metric",
            value_name="rate",
        )
        end_long["metric"] = end_long["metric"].map(
            {
                "hallucination_detected": "Detected",
                "endorsed_hallucination": "Endorsed",
            }
        )
        fig4 = px.bar(
            end_long,
            x="model_label",
            y="rate",
            color="metric",
            barmode="group",
            text=end_long["rate"].map("{:.1f}%".format),
            color_discrete_map={"Detected": "#e74c3c", "Endorsed": "#c0392b"},
            labels={"model_label": "Model", "rate": "%", "metric": ""},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=360)
        st.plotly_chart(fig4, width='stretch')

    st.divider()
    st.subheader("Metric correlation matrix")
    st.caption("Correlation between key performance metrics across all trials")
    
    # Calculate correlation matrix
    metrics_cols = [
        "hallucination_detected",
        "endorsed_hallucination",
        "adoption_rate_failure",
        "detection_rate_success",
        "dangerous_reasoning_hallucination",
    ]
    corr_df = fdf[metrics_cols].corr()
    
    # Create heatmap
    fig_corr = go.Figure(
        go.Heatmap(
            z=corr_df.values,
            x=[col.replace("_", " ").title() for col in corr_df.columns],
            y=[col.replace("_", " ").title() for col in corr_df.index],
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr_df.values],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Correlation"),
        )
    )
    fig_corr.update_layout(
        margin=dict(l=100, r=30, t=30, b=30),
        height=400,
    )
    st.plotly_chart(fig_corr, width='stretch')

    st.divider()
    st.subheader("Distribution analysis by model")
    st.caption("Violin plots showing distribution of hallucination detection rates across models")
    
    # Create violin plot for detection rates
    box_df = fdf.copy()
    box_df["model_label"] = box_df["model_full"].map(model_label)
    
    fig_box = go.Figure()
    for model in box_df["model_label"].unique():
        model_data = box_df[box_df["model_label"] == model]["detection_rate_success"]
        fig_box.add_trace(
            go.Violin(
                y=model_data,
                name=model,
                marker_color=MODEL_COLORS.get(
                    box_df[box_df["model_label"] == model]["model_full"].iloc[0], "#888"
                ),
                box_visible=True,
                meanline_visible=True,
            )
        )
    fig_box.update_layout(
        yaxis=dict(title="Detection success rate", range=[0, 1]),
        xaxis=dict(title=""),
        margin=dict(l=0, r=30, t=10, b=10),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_box, width='stretch')

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LEADERBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Model × condition leaderboard")
    st.caption(
        "Ranked by defense rate ↑, adoption rate ↓, dangerous reasoning ↓, sample size ↑"
    )

    if dashboard_json and set(sel_models) == set(all_models) and set(sel_conditions) == set(all_conditions):
        leaderboard = pd.DataFrame(dashboard_json["leaderboard"])
        leaderboard["model_label"] = leaderboard["model"].map(model_label)
    else:
        leaderboard = build_leaderboard(fdf)

    leaderboard_display = leaderboard.copy()
    for col in (
        "successful_defense_rate",
        "silent_adoption_rate",
        "false_positive_rate",
        "blind_spot_rate",
        "dangerous_reasoning_hallucination_rate",
    ):
        if col in leaderboard_display.columns:
            leaderboard_display[col] = leaderboard_display[col].map(lambda v: pct(v))

    show_cols = [
        c
        for c in [
            "rank",
            "model_label" if "model_label" in leaderboard_display.columns else "model",
            "condition",
            "total_trials",
            "successful_defense_rate",
            "silent_adoption_rate",
            "false_positive_rate",
            "blind_spot_rate",
            "dangerous_reasoning_hallucination_rate",
        ]
        if c in leaderboard_display.columns
    ]
    
    paginated_df, current_page, total_pages = paginate_dataframe(
        leaderboard_display[show_cols].rename(
            columns={
                "rank": "Rank",
                "model_label": "Model",
                "model": "Model",
                "condition": "Condition",
                "total_trials": "n",
                "successful_defense_rate": "Defense",
                "silent_adoption_rate": "Adopted",
                "false_positive_rate": "False pos.",
                "blind_spot_rate": "Blind spot",
                "dangerous_reasoning_hallucination_rate": "Dangerous",
            }
        ),
        page_size=15
    )
    st.dataframe(
        paginated_df,
        width='stretch',
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "Model": st.column_config.TextColumn("Model"),
            "Condition": st.column_config.TextColumn("Condition"),
            "n": st.column_config.NumberColumn("n", format="%d"),
            "Defense": st.column_config.TextColumn("Defense"),
            "Adopted": st.column_config.TextColumn("Adopted"),
            "False pos.": st.column_config.TextColumn("False pos."),
            "Blind spot": st.column_config.TextColumn("Blind spot"),
            "Dangerous": st.column_config.TextColumn("Dangerous"),
        }
    )
    if total_pages > 1:
        st.caption(f"Showing page {current_page} of {total_pages} ({len(leaderboard_display)} total rows)")

    st.subheader("Defense vs adoption by model × condition")
    scatter_df = leaderboard.copy()
    scatter_df["model_label"] = scatter_df.get("model", scatter_df.get("model_full")).map(
        lambda value: model_label(value) if isinstance(value, str) else value
    )
    if "model" in scatter_df.columns:
        scatter_df["color_key"] = scatter_df["model"]
    else:
        scatter_df["color_key"] = scatter_df["model_full"]

    fig_lb = px.scatter(
        scatter_df,
        x="silent_adoption_rate",
        y="successful_defense_rate",
        color="color_key",
        symbol="condition",
        size="total_trials",
        hover_data=["condition", "total_trials"],
        labels={
            "silent_adoption_rate": "Silent adoption rate",
            "successful_defense_rate": "Successful defense rate",
            "color_key": "Model",
            "condition": "Condition",
        },
        color_discrete_map=MODEL_COLORS,
    )
    fig_lb.update_layout(
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        margin=dict(l=0, r=0, t=10, b=10),
        height=420,
        legend=dict(title="Model"),
    )
    st.plotly_chart(fig_lb, width='stretch')

    if dashboard_json and set(sel_models) == set(all_models):
        st.subheader("Model summary")
        model_summary = pd.DataFrame(dashboard_json["by_model"])
        model_summary["model_label"] = model_summary["model"].map(model_label)
        summary_display = model_summary[
            [
                "model_label",
                "total_trials",
                "successful_defense_rate",
                "silent_adoption_rate",
                "false_positive_rate",
                "blind_spot_rate",
            ]
        ].copy()
        for col in summary_display.columns[2:]:
            summary_display[col] = summary_display[col].map(pct)
        st.dataframe(
            summary_display.rename(
                columns={
                    "model_label": "Model",
                    "total_trials": "n",
                    "successful_defense_rate": "Defense",
                    "silent_adoption_rate": "Adopted",
                    "false_positive_rate": "False pos.",
                    "blind_spot_rate": "Blind spot",
                }
            ),
            width='stretch',
            hide_index=True,
            column_config={
                "Model": st.column_config.TextColumn("Model"),
                "n": st.column_config.NumberColumn("n", format="%d"),
                "Defense": st.column_config.TextColumn("Defense"),
                "Adopted": st.column_config.TextColumn("Adopted"),
                "False pos.": st.column_config.TextColumn("False pos."),
                "Blind spot": st.column_config.TextColumn("Blind spot"),
            }
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CONDITION EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Hallucination rate by model × condition (95% CI)")
    fig5 = go.Figure()
    for cond in ["DEFAULT", "DETERMINISTIC", "SAFETY_INSTRUCTION"]:
        sub = ft2[ft2["condition"] == cond].sort_values("model_full").copy()
        sub["model_label"] = sub["model_full"].map(model_label)
        fig5.add_trace(
            go.Bar(
                name=cond,
                x=sub["model_label"],
                y=sub["hallucination_rate_pct"],
                error_y=dict(
                    type="data",
                    symmetric=False,
                    array=(sub["hall_ci_high_pct"] - sub["hallucination_rate_pct"]).tolist(),
                    arrayminus=(sub["hallucination_rate_pct"] - sub["hall_ci_low_pct"]).tolist(),
                    color="#333",
                    thickness=1.5,
                ),
                marker_color=CONDITION_COLORS.get(cond, "#888"),
                text=sub["hallucination_rate_pct"].map("{:.1f}%".format),
                textposition="outside",
            )
        )
    fig5.update_layout(
        barmode="group",
        yaxis=dict(title="Hallucination rate (%)", range=[0, 115]),
        margin=dict(l=0, r=0, t=10, b=10),
        height=400,
    )
    st.plotly_chart(fig5, width='stretch')

    st.subheader("Outcome mix by condition")
    cond_cat = (
        fdf.groupby(["condition", "category"]).size().reset_index(name="count")
    )
    cond_totals = cond_cat.groupby("condition")["count"].transform("sum")
    cond_cat["pct"] = cond_cat["count"] / cond_totals * 100
    fig_cond = px.bar(
        cond_cat,
        x="condition",
        y="pct",
        color="category",
        barmode="stack",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"category": CATEGORY_ORDER},
        text=cond_cat["pct"].map("{:.1f}%".format),
        labels={"condition": "Condition", "pct": "%", "category": "Outcome"},
    )
    fig_cond.update_traces(textposition="inside")
    fig_cond.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=320)
    st.plotly_chart(fig_cond, width='stretch')

    st.subheader("Condition effect — percentage difference vs DEFAULT")
    st.caption("Positive = higher hallucination rate than DEFAULT; negative = lower")
    rr_display = ft3[
        [
            "model_full",
            "comparison",
            "default_rate_pct",
            "comparison_rate_pct",
            "risk_difference_pct",
        ]
    ].copy()
    rr_display["Model"] = rr_display["model_full"].map(model_label)
    rr_display["Direction"] = rr_display["risk_difference_pct"].apply(
        lambda v: "↑ Worse" if v > 0 else "↓ Better" if v < 0 else "— Same"
    )
    rr_display["Sig."] = rr_display.apply(
        lambda r: calculate_significance_indicator(r.get('rr_ci_low'), r.get('rr_ci_high'))[1],
        axis=1
    )
    st.dataframe(
        rr_display[
            [
                "Model",
                "comparison",
                "default_rate_pct",
                "comparison_rate_pct",
                "risk_difference_pct",
                "Direction",
                "Sig.",
            ]
        ].rename(
            columns={
                "comparison": "Comparison",
                "default_rate_pct": "DEFAULT %",
                "comparison_rate_pct": "Comparison %",
                "risk_difference_pct": "Diff %",
                "Sig.": "Sig.",
            }
        ),
        width='stretch',
        hide_index=True,
        column_config={
            "Model": st.column_config.TextColumn("Model"),
            "Comparison": st.column_config.TextColumn("Comparison"),
            "DEFAULT %": st.column_config.TextColumn("DEFAULT %"),
            "Comparison %": st.column_config.TextColumn("Comparison %"),
            "Diff %": st.column_config.TextColumn("Diff %"),
            "Direction": st.column_config.TextColumn("Direction"),
            "Sig.": st.column_config.TextColumn("Sig."),
        }
    )

    st.subheader("Adoption failure rate by model × condition")
    ft2_plot = ft2.copy()
    ft2_plot["model_label"] = ft2_plot["model_full"].map(model_label)
    fig6 = px.bar(
        ft2_plot,
        x="model_label",
        y="adoption_failure_rate_pct",
        color="condition",
        barmode="group",
        text=ft2_plot["adoption_failure_rate_pct"].map("{:.1f}%".format),
        color_discrete_map=CONDITION_COLORS,
        labels={"model_label": "Model", "adoption_failure_rate_pct": "%", "condition": "Condition"},
    )
    fig6.update_traces(textposition="outside")
    fig6.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=340)
    st.plotly_chart(fig6, width='stretch')

    st.subheader("Hallucination rate heatmap — model × condition")
    pivot = (
        fdf.groupby(["model_full", "condition"])["hallucination_detected"]
        .mean()
        .mul(100)
        .unstack(fill_value=0)
    )
    pivot.index = pivot.index.map(model_label)
    fig7 = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="RdYlGn_r",
            zmin=0,
            zmax=100,
            text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            colorbar=dict(title="%"),
        )
    )
    fig7.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=max(260, 60 * len(pivot)))
    st.plotly_chart(fig7, width='stretch')

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LENGTH EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Short vs long vignette — hallucination rate (95% CI)")
    fig8 = go.Figure()
    for _, row in ft4.iterrows():
        label = f"{model_label(row['model_full'])} · {row['condition']}"
        fig8.add_trace(
            go.Scatter(
                x=["Short", "Long"],
                y=[row["short_rate_pct"], row["long_rate_pct"]],
                mode="lines+markers",
                name=label,
                line=dict(
                    color=MODEL_COLORS.get(row["model_full"], "#888"),
                    dash="solid"
                    if row["condition"] == "DEFAULT"
                    else "dash"
                    if row["condition"] == "DETERMINISTIC"
                    else "dot",
                ),
                marker=dict(size=8),
            )
        )
    fig8.update_layout(
        yaxis=dict(title="Hallucination rate (%)", range=[0, 105]),
        xaxis=dict(title="Vignette length"),
        margin=dict(l=0, r=0, t=10, b=10),
        height=420,
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig8, width='stretch')

    st.subheader("Percentage difference: short − long")
    st.caption("Positive = more hallucinations in short vignettes; negative = more in long")
    ft4_plot = ft4.copy()
    ft4_plot["model_label"] = ft4_plot["model_full"].map(model_label)
    ft4_plot["Sig."] = ft4_plot.apply(
        lambda r: calculate_significance_indicator(r.get('rr_ci_low'), r.get('rr_ci_high'))[1],
        axis=1
    )
    fig9 = px.bar(
        ft4_plot,
        x="model_label",
        y="risk_difference_pct",
        color="condition",
        barmode="group",
        color_discrete_map=CONDITION_COLORS,
        text=ft4_plot["risk_difference_pct"].map("{:+.1f}%".format),
        labels={"model_label": "Model", "risk_difference_pct": "Diff (%)", "condition": "Condition"},
    )
    fig9.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
    fig9.update_traces(textposition="outside")
    fig9.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=360)
    st.plotly_chart(fig9, width='stretch')

    st.subheader("Silent adoption by vignette length")
    len_cat = (
        fdf.groupby(["vignette_length", "category"]).size().reset_index(name="count")
    )
    len_totals = len_cat.groupby("vignette_length")["count"].transform("sum")
    len_cat["pct"] = len_cat["count"] / len_totals * 100
    fig_len = px.bar(
        len_cat,
        x="vignette_length",
        y="pct",
        color="category",
        barmode="stack",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"category": CATEGORY_ORDER},
        text=len_cat["pct"].map("{:.1f}%".format),
        labels={"vignette_length": "Length", "pct": "%", "category": "Outcome"},
    )
    fig_len.update_traces(textposition="inside")
    fig_len.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=300)
    st.plotly_chart(fig_len, width='stretch')

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TOKEN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Outcomes by fabricated token category")
    token_df = fdf.copy()
    token_df["token_category_label"] = token_df["token_category"].map(
        lambda value: TOKEN_CATEGORY_LABELS.get(value, value.replace("_", " ").title())
    )
    token_cat = (
        token_df.groupby(["token_category_label", "category"]).size().reset_index(name="count")
    )
    token_totals = token_cat.groupby("token_category_label")["count"].transform("sum")
    token_cat["pct"] = token_cat["count"] / token_totals * 100
    fig_token = px.bar(
        token_cat,
        x="token_category_label",
        y="pct",
        color="category",
        barmode="stack",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"category": CATEGORY_ORDER},
        labels={"token_category_label": "Token category", "pct": "%", "category": "Outcome"},
    )
    fig_token.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=360)
    st.plotly_chart(fig_token, width='stretch')

    left, right = st.columns(2)

    with left:
        st.subheader("Silent adoption rate by token category")
        adopt_by_token = (
            token_df.groupby("token_category_label")["adoption_rate_failure"]
            .mean()
            .mul(100)
            .reset_index(name="rate")
            .sort_values("rate", ascending=False)
        )
        fig_adopt = px.bar(
            adopt_by_token,
            x="token_category_label",
            y="rate",
            text=adopt_by_token["rate"].map("{:.1f}%".format),
            labels={"token_category_label": "Token category", "rate": "Adoption failure %"},
        )
        fig_adopt.update_traces(marker_color="#f39c12", textposition="outside")
        fig_adopt.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=320)
        st.plotly_chart(fig_adopt, width='stretch')

    with right:
        st.subheader("Detection success by token category")
        detect_by_token = (
            token_df.groupby("token_category_label")["detection_rate_success"]
            .mean()
            .mul(100)
            .reset_index(name="rate")
            .sort_values("rate", ascending=True)
        )
        fig_detect = px.bar(
            detect_by_token,
            x="token_category_label",
            y="rate",
            text=detect_by_token["rate"].map("{:.1f}%".format),
            labels={"token_category_label": "Token category", "rate": "Detection success %"},
        )
        fig_detect.update_traces(marker_color="#2ecc71", textposition="outside")
        fig_detect.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=320)
        st.plotly_chart(fig_detect, width='stretch')

    st.subheader("Hardest fabricated tokens")
    st.caption("Highest silent adoption rate across filtered trials (minimum 4 trials)")
    token_summary = (
        token_df.groupby(["token_text", "token_category_label"])
        .agg(
            trials=("case_id", "count"),
            adoption_rate=("adoption_rate_failure", "mean"),
            defense_rate=("category", lambda s: (s == "Successful Defense").mean()),
        )
        .reset_index()
    )
    token_summary = token_summary[token_summary["trials"] >= 4].sort_values(
        "adoption_rate", ascending=False
    )
    token_summary["adoption_rate"] = token_summary["adoption_rate"].map(pct)
    token_summary["defense_rate"] = token_summary["defense_rate"].map(pct)
    st.dataframe(
        token_summary.head(15).rename(
            columns={
                "token_text": "Fabricated token",
                "token_category_label": "Category",
                "trials": "Trials",
                "adoption_rate": "Adoption failure",
                "defense_rate": "Defense rate",
            }
        ),
        width='stretch',
        hide_index=True,
        column_config={
            "Fabricated token": st.column_config.TextColumn("Fabricated token"),
            "Category": st.column_config.TextColumn("Category"),
            "Trials": st.column_config.NumberColumn("Trials", format="%d"),
            "Adoption failure": st.column_config.TextColumn("Adoption failure"),
            "Defense rate": st.column_config.TextColumn("Defense rate"),
        }
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CASE EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    explorer_condition = st.selectbox(
        "Condition for case heatmap",
        options=all_conditions,
        index=all_conditions.index("DEFAULT") if "DEFAULT" in all_conditions else 0,
    )
    explorer_length = st.selectbox(
        "Vignette length for case heatmap",
        options=all_lengths,
        index=all_lengths.index("short") if "short" in all_lengths else 0,
    )
    
    search_query = st.text_input("🔍 Search cases (by case ID or token text)", placeholder="e.g., CASE_001 or amoxicillin")

    st.subheader("Per-case outcome heatmap")
    st.caption(
        f"{explorer_condition} · {explorer_length} · "
        f"{len(sel_models)} selected model(s). Sorted by average outcome (hardest first)."
    )

    heat_df = fdf[
        (fdf["condition"] == explorer_condition)
        & (fdf["vignette_length"] == explorer_length)
    ][["case_id", "model_full", "category", "token_text"]].copy()
    
    # Apply search filter if provided
    if search_query:
        search_query = search_query.lower()
        heat_df = heat_df[
            heat_df["case_id"].str.lower().str.contains(search_query, na=False) |
            heat_df["token_text"].str.lower().str.contains(search_query, na=False)
        ]

    if heat_df.empty:
        st.info("No trials match the current filters.")
    else:
        heat_df["cat_num"] = heat_df["category"].map(CATEGORY_NUM)
        pivot_heat = heat_df.pivot_table(
            index="case_id", columns="model_full", values="cat_num", aggfunc="first"
        )
        pivot_heat.columns = [model_label(col) for col in pivot_heat.columns]
        pivot_heat = pivot_heat.loc[pivot_heat.mean(axis=1).sort_values().index]

        colorscale = [
            [0.0, CATEGORY_COLORS["Silent Adoption"]],
            [0.33, CATEGORY_COLORS["False Positive"]],
            [0.66, CATEGORY_COLORS["Blind Spot"]],
            [1.0, CATEGORY_COLORS["Successful Defense"]],
        ]
        fig10 = go.Figure(
            go.Heatmap(
                z=pivot_heat.values,
                x=pivot_heat.columns.tolist(),
                y=pivot_heat.index.tolist(),
                colorscale=colorscale,
                zmin=0,
                zmax=3,
                colorbar=dict(
                    tickvals=[0, 1, 2, 3],
                    ticktext=["Silent Adoption", "False Positive", "Blind Spot", "Successful Defense"],
                    title="Outcome",
                ),
            )
        )
        fig10.update_layout(
            height=min(900, max(420, 12 * len(pivot_heat))),
            margin=dict(l=0, r=0, t=10, b=10),
            yaxis=dict(showticklabels=False, title="Cases"),
        )
        st.plotly_chart(fig10, width='stretch')

        n_models_selected = heat_df["model_full"].nunique()
        fail_label = f"Cases where all {n_models_selected} models failed (Silent Adoption)"
        win_label = f"Cases where all {n_models_selected} models succeeded (Successful Defense)"

        c_fail, c_win = st.columns(2)
        with c_fail:
            st.subheader(fail_label)
            all_fail = heat_df.groupby("case_id")["category"].apply(
                lambda values: (values == "Silent Adoption").all()
            )
            failed_cases = all_fail[all_fail].index.tolist()
            st.metric("Count", len(failed_cases))
            if failed_cases:
                st.dataframe(pd.DataFrame({"case_id": failed_cases}), hide_index=True)

        with c_win:
            st.subheader(win_label)
            all_win = heat_df.groupby("case_id")["category"].apply(
                lambda values: (values == "Successful Defense").all()
            )
            won_cases = all_win[all_win].index.tolist()
            st.metric("Count", len(won_cases))
            if won_cases:
                st.dataframe(pd.DataFrame({"case_id": won_cases}), hide_index=True)

        st.subheader("Single-case lookup")
        case_options = sorted(heat_df["case_id"].unique())
        selected_case = st.selectbox("Case ID", case_options)
        case_rows = fdf[fdf["case_id"] == selected_case].copy()
        case_rows["model_label"] = case_rows["model_full"].map(model_label)
        if not case_rows.empty:
            st.write(f"**Fabricated token:** {case_rows['token_text'].iloc[0]}")
            st.dataframe(
                case_rows[
                    [
                        "model_label",
                        "condition",
                        "vignette_length",
                        "category",
                        "hallucination_detected",
                        "adoption_rate_failure",
                        "detection_rate_success",
                    ]
                ].rename(
                    columns={
                        "model_label": "Model",
                        "condition": "Condition",
                        "vignette_length": "Length",
                        "category": "Outcome",
                        "hallucination_detected": "Flagged",
                        "adoption_rate_failure": "Adopted fake term",
                        "detection_rate_success": "Detected",
                    }
                ),
                width='stretch',
                hide_index=True,
            )

    with st.expander("Raw trial data"):
        export_df = fdf.copy()
        export_df["model_label"] = export_df["model_full"].map(model_label)
        trial_cols = [
            "model_label",
            "condition",
            "vignette_length",
            "case_id",
            "token_text",
            "token_category",
            "hallucination_detected",
            "endorsed_hallucination",
            "adoption_rate_failure",
            "detection_rate_success",
            "dangerous_reasoning_hallucination",
            "category",
        ]
        
        paginated_trials, current_page, total_pages = paginate_dataframe(
            export_df[trial_cols],
            page_size=50
        )
        st.dataframe(
            paginated_trials,
            width='stretch',
            height=380,
        )
        if total_pages > 1:
            st.caption(f"Showing page {current_page} of {total_pages} ({len(export_df):,} total rows)")
        else:
            st.caption(f"{len(export_df):,} rows")
        st.download_button(
            "Download filtered trials",
            export_df.to_csv(index=False),
            "pahs_filtered_trials.csv",
            "text/csv",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — PUBLICATION TABLES
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.subheader("Table 1 — Trial coverage by model")
    t1_display = ft1.copy()
    t1_display["model_label"] = t1_display["model_full"].map(model_label)
    st.dataframe(
        t1_display.drop(columns=["provider", "model_name", "model_full"]).rename(
            columns={"model_label": "model"}
        ),
        width='stretch',
        hide_index=True,
        column_config={
            "model": st.column_config.TextColumn("model"),
            "total_trials": st.column_config.NumberColumn("total_trials", format="%d"),
            "hallucination_rate_pct": st.column_config.TextColumn("hallucination_rate_pct"),
            "endorsed_hallucination_rate_pct": st.column_config.TextColumn("endorsed_hallucination_rate_pct"),
            "adoption_failure_rate_pct": st.column_config.TextColumn("adoption_failure_rate_pct"),
            "detection_success_rate_pct": st.column_config.TextColumn("detection_success_rate_pct"),
            "dangerous_reasoning_rate_pct": st.column_config.TextColumn("dangerous_reasoning_rate_pct"),
        }
    )
    st.download_button("Download Table 1", ft1.to_csv(index=False), "table1_coverage.csv", "text/csv")

    st.divider()
    st.subheader("Table 2 — Hallucination outcomes by model × condition")
    t2_display = ft2.copy()
    t2_display["model_label"] = t2_display["model_full"].map(model_label)
    t2_display["95% CI"] = t2_display.apply(
        lambda r: f"[{r['hall_ci_low_pct']:.1f}%, {r['hall_ci_high_pct']:.1f}%]", axis=1
    )
    st.dataframe(
        t2_display[
            [
                "model_label",
                "condition",
                "n",
                "hallucination_rate_pct",
                "95% CI",
                "endorsed_hallucination_rate_pct",
                "adoption_failure_rate_pct",
                "detection_success_rate_pct",
                "dangerous_reasoning_rate_pct",
            ]
        ].rename(
            columns={
                "model_label": "Model",
                "condition": "Condition",
                "n": "n",
                "hallucination_rate_pct": "Hall. rate %",
                "endorsed_hallucination_rate_pct": "Endorsed %",
                "adoption_failure_rate_pct": "Adoption fail %",
                "detection_success_rate_pct": "Detection %",
                "dangerous_reasoning_rate_pct": "Dangerous %",
            }
        ),
        width='stretch',
        hide_index=True,
    )
    st.download_button("Download Table 2", ft2.to_csv(index=False), "table2_outcomes.csv", "text/csv")

    st.divider()
    st.subheader("Table 3 — Condition effects vs DEFAULT")
    t3_display = ft3.copy()
    t3_display["Model"] = t3_display["model_full"].map(model_label)
    t3_display["Direction"] = t3_display["risk_difference_pct"].apply(
        lambda v: "↑ Worse" if v > 0 else "↓ Better" if v < 0 else "— Same"
    )
    st.dataframe(
        t3_display[
            ["Model", "comparison", "default_rate_pct", "comparison_rate_pct", "risk_difference_pct", "Direction"]
        ].rename(
            columns={
                "comparison": "Comparison",
                "default_rate_pct": "DEFAULT %",
                "comparison_rate_pct": "Comparison %",
                "risk_difference_pct": "Diff %",
            }
        ),
        width='stretch',
        hide_index=True,
    )
    st.download_button("Download Table 3", ft3.to_csv(index=False), "table3_condition_effects.csv", "text/csv")

    st.divider()
    st.subheader("Table 4 — Length effects (short vs long)")
    t4_display = ft4.copy()
    t4_display["Model"] = t4_display["model_full"].map(model_label)
    t4_display["Direction"] = t4_display["risk_difference_pct"].apply(
        lambda v: "↑ More in short" if v > 0 else "↓ More in long" if v < 0 else "— Same"
    )
    st.dataframe(
        t4_display[
            [
                "Model",
                "condition",
                "short_n",
                "short_rate_pct",
                "long_n",
                "long_rate_pct",
                "risk_difference_pct",
                "Direction",
            ]
        ].rename(
            columns={
                "condition": "Condition",
                "short_n": "Short n",
                "short_rate_pct": "Short %",
                "long_n": "Long n",
                "long_rate_pct": "Long %",
                "risk_difference_pct": "Diff %",
            }
        ),
        width='stretch',
        hide_index=True,
    )
    st.download_button("Download Table 4", ft4.to_csv(index=False), "table4_length_effects.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — HELP & GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
with tab8:
    st.header("How to Study Each Model")
    
    st.markdown("""
    This guide will help you systematically analyze and compare the performance of different LLMs in detecting hallucinations.
    """)
    
    st.divider()
    
    st.subheader("Step 1: Understand the Outcome Categories")
    st.markdown("""
    | Category | What happened | Clinical risk | Interpretation |
    | --- | --- | --- | --- |
    | **Successful Defense** | Fake term detected and excluded | None — goal behavior | Model correctly identified the fabricated term |
    | **Silent Adoption** | Fake term accepted as real | **High** — hallucination in reasoning | Model hallucinated, accepted fake information |
    | **False Positive** | Real term wrongly flagged as fake | Moderate — alert fatigue | Model was overly suspicious, flagged real term |
    | **Blind Spot** | Fake term ignored, neither adopted nor flagged | Low–moderate — noise unnoticed | Model missed the fake term entirely |
    """)
    
    st.divider()
    
    st.subheader("Step 2: Key Metrics to Study")
    st.markdown("""
    **Primary Metrics:**
    - **Detection Success Rate**: Percentage of trials where the model detected the fake term
    - **Adoption Failure Rate**: Percentage of trials where the model adopted the fake term (Silent Adoption)
    - **Hallucination Detected**: Whether the model flagged the presence of hallucination
    - **Dangerous Reasoning**: Whether the hallucination led to clinically dangerous reasoning
    
    **Secondary Metrics:**
    - **False Positive Rate**: How often the model incorrectly flags real terms as fake
    - **Blind Spot Rate**: How often the model misses fake terms entirely
    """)
    
    st.divider()
    
    st.subheader("Step 3: How to Analyze a Specific Model")
    st.markdown("""
    **Method 1: Using the Overview Tab**
    1. Go to the **Overview** tab
    2. Use the sidebar filters to select only your model of interest
    3. Review the KPI metrics at the top
    4. Examine the "Hallucination rate by model" chart
    5. Check the "Outcome categories by model" stacked bar
    6. Review the "Model safety profile" radar chart
    
    **Method 2: Using the Leaderboard Tab**
    1. Go to the **Leaderboard** tab
    2. Find your model in the leaderboard table
    3. Compare its rank across different conditions
    4. Review the "Defense vs adoption" scatter plot to see relative performance
    """)
    
    st.divider()
    
    st.subheader("Step 4: Comparing Models")
    st.markdown("""
    **Side-by-Side Comparison:**
    1. Use the sidebar to select 2-3 models you want to compare
    2. Go to the **Overview** tab to see overall performance comparison
    3. Check the **Leaderboard** tab for ranked comparison
    4. Review **Condition Effects** to see how models respond to different prompts
    5. Check **Length Effects** to see performance on short vs long vignettes
    
    **Key Comparison Points:**
    - Which model has the highest detection success rate?
    - Which model has the lowest silent adoption rate?
    - How do models perform under different conditions (DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC)?
    - Are there differences in performance between short and long vignettes?
    """)
    
    st.divider()
    
    st.subheader("Step 5: Deep Dive Analysis")
    st.markdown("""
    **Condition Effects Analysis:**
    - Go to **Condition Effects** tab
    - Study how each model responds to safety instructions
    - Check if deterministic prompts reduce hallucinations
    - Look at the risk ratios to see effect sizes
    
    **Token Category Analysis:**
    - Go to **Token Analysis** tab
    - See which types of fabricated terms are hardest for each model
    - Check if certain categories (e.g., lab markers, drugs) are more problematic
    
    **Case-Level Analysis:**
    - Go to **Case Explorer** tab
    - Search for specific cases or tokens
    - Use the heatmap to see which cases are hardest for all models
    - Review individual case details to understand failure modes
    """)
    
    st.divider()
    
    st.subheader("Step 6: Statistical Interpretation")
    st.markdown("""
    **Confidence Intervals (CI):**
    - 95% CI shows the range where the true value likely falls
    - Narrow CI = more precise estimate
    - Wide CI = less certainty, usually due to small sample size
    
    **Statistical Significance (Sig.):**
    - *** = Statistically significant (CI does not include null value)
    - Blank = Not statistically significant
    - For risk ratios: significant if CI does not include 1.0
    - For risk differences: significant if CI does not include 0
    
    **Correlation Matrix:**
    - Shows relationships between metrics
    - Values close to 1.0 = strong positive correlation
    - Values close to -1.0 = strong negative correlation
    - Values close to 0 = no correlation
    """)
    
    st.divider()
    
    st.subheader("Step 7: Practical Tips")
    st.markdown("""
    **For Clinical Decision Making:**
    - Prioritize models with high detection success and low silent adoption
    - Consider false positive rates - too many may cause alert fatigue
    - Look at dangerous reasoning rates - these are most clinically relevant
    
    **For Research:**
    - Use the Publication Tables tab for export-ready data
    - Download charts as PNG/SVG for papers
    - Generate summary reports for documentation
    
    **For Model Selection:**
    - Consider the trade-off between detection and false positives
    - Evaluate performance across different conditions
    - Check if the model performs consistently across vignette lengths
    """)
    
    st.divider()
    
    st.subheader("Step 8: Study Workflow Example")
    st.markdown("""
    **Example: Studying Claude Haiku 4.5**
    
    1. **Start with Overview**: Filter to Claude Haiku 4.5, note overall metrics
    2. **Check Leaderboard**: See its rank compared to other models
    3. **Review Conditions**: How does it respond to safety instructions?
    4. **Analyze Length**: Performance on short vs long vignettes
    5. **Token Analysis**: Which token categories are problematic?
    6. **Case Explorer**: Look at specific failure cases
    7. **Export Data**: Download relevant tables for further analysis
    8. **Generate Report**: Use the summary report for documentation
    """)
    
    st.divider()
    
    st.subheader("Frequently Asked Questions")
    
    with st.expander("What is a 'good' detection rate?"):
        st.markdown("""
        A good detection rate depends on the use case:
        - **For clinical safety**: Aim for >80% detection success
        - **For research**: Compare relative performance between models
        - **For general use**: Balance detection with false positive rate
        """)
    
    with st.expander("Why do some models show no variation in box plots?"):
        st.markdown("""
        Some models may have consistent performance across trials, showing little variation.
        This could indicate:
        - Consistent behavior (good or bad)
        - Small sample size
        - Model limitations in handling the task
        """)
    
    with st.expander("How do I interpret the risk ratio?"):
        st.markdown("""
        - **RR > 1.0**: Higher risk than baseline (worse)
        - **RR < 1.0**: Lower risk than baseline (better)
        - **RR = 1.0**: No difference from baseline
        - Example: RR = 0.5 means 50% reduction in risk
        """)
    
    with st.expander("What should I do if I see high silent adoption?"):
        st.markdown("""
        High silent adoption indicates the model is hallucinating frequently.
        Consider:
        - Adding safety instructions to prompts
        - Using deterministic prompts
        - Switching to a different model
        - Implementing additional validation steps
        """)
    
    st.success("You're now ready to systematically study and compare LLM performance!")
    
    st.divider()
    
    st.header("Diagram Instructions")
    
    st.subheader("Overview Tab Diagrams")
    
    with st.expander("Hallucination Rate by Model (95% CI)"):
        st.markdown("""
        **What it shows:** Bar chart showing hallucination rate for each model with 95% confidence intervals
        
        **How to read it:**
        - Bar height = hallucination rate percentage
        - Error bars = 95% confidence interval (range of uncertainty)
        - Lower bars = better performance (less hallucination)
        
        **What to look for:**
        - Which model has the lowest hallucination rate?
        - Are confidence intervals narrow (precise) or wide (uncertain)?
        - Do confidence intervals overlap between models?
        """)
    
    with st.expander("Outcome Category Distribution"):
        st.markdown("""
        **What it shows:** Pie chart showing the proportion of each outcome category
        
        **How to read it:**
        - Slice size = percentage of trials in that category
        - Green (Successful Defense) = good
        - Orange (Silent Adoption) = bad (hallucination)
        - Red (Blind Spot) = moderate concern
        - Purple (False Positive) = moderate concern
        
        **What to look for:**
        - High green = model detects fake terms well
        - High orange = model hallucinates frequently
        - Balance between categories
        """)
    
    with st.expander("Outcome Categories by Model (Stacked %)"):
        st.markdown("""
        **What it shows:** Stacked bar chart showing outcome distribution for each model
        
        **How to read it:**
        - Each bar = one model
        - Bar segments = outcome categories
        - Segment height = percentage of trials in that category
        - Total bar height = 100%
        
        **What to look for:**
        - Compare green segments (Successful Defense) across models
        - Compare orange segments (Silent Adoption) across models
        - Which model has the best distribution?
        """)
    
    with st.expander("Model Safety Profile (Radar Chart)"):
        st.markdown("""
        **What it shows:** Radar chart comparing models across 4 safety metrics
        
        **How to read it:**
        - Each axis = one metric (Defense, Low adoption, Detection, Low blind spot)
        - Points closer to edge = better performance
        - Larger shape = overall better performance
        - Shape symmetry = balanced performance
        
        **What to look for:**
        - Which model has the largest area?
        - Are models strong in some areas but weak in others?
        - Which model has the most balanced profile?
        """)
    
    with st.expander("Detected vs Endorsed Hallucination"):
        st.markdown("""
        **What it shows:** Grouped bar chart comparing detection vs endorsement rates
        
        **How to read it:**
        - Red bars (Detected) = hallucination was flagged
        - Dark red bars (Endorsed) = model agreed with fake term
        - Lower bars = better (less hallucination)
        
        **What to look for:**
        - Which model detects most hallucinations?
        - Which model endorses fewest hallucinations?
        - Gap between detected and endorsed
        """)
    
    with st.expander("Metric Correlation Matrix"):
        st.markdown("""
        **What it shows:** Heatmap showing correlations between metrics
        
        **How to read it:**
        - Color intensity = correlation strength
        - Red = positive correlation (metrics move together)
        - Blue = negative correlation (metrics move opposite)
        - Values range from -1 to +1
        
        **What to look for:**
        - Strong correlations (|value| > 0.7)
        - Unexpected relationships between metrics
        - Which metrics are independent of each other
        """)
    
    with st.expander("Distribution Analysis (Violin Plot)"):
        st.markdown("""
        **What it shows:** Violin plots showing distribution of detection rates
        
        **How to read it:**
        - Shape width = frequency of values at that rate
        - Box inside = quartiles (25%, 50%, 75%)
        - White dot = median
        - Height = range of values
        
        **What to look for:**
        - Which model has highest median detection rate?
        - Which model has most consistent performance (narrow shape)?
        - Which model has most variable performance (wide shape)?
        - Outliers (individual points beyond box)
        """)
    
    st.divider()
    
    st.subheader("Leaderboard Tab Diagrams")
    
    with st.expander("Model × Condition Leaderboard"):
        st.markdown("""
        **What it shows:** Ranked table of model performance by condition
        
        **How to read it:**
        - Rank = overall performance ranking
        - Defense = Successful Defense rate (higher is better)
        - Adopted = Silent Adoption rate (lower is better)
        - Dangerous = Dangerous reasoning rate (lower is better)
        
        **What to look for:**
        - Which model-condition combination ranks highest?
        - How does a model perform across different conditions?
        - Which condition yields best performance for each model?
        """)
    
    with st.expander("Defense vs Adoption Scatter Plot"):
        st.markdown("""
        **What it shows:** Scatter plot comparing defense vs adoption rates
        
        **How to read it:**
        - X-axis = Silent Adoption rate (lower is better)
        - Y-axis = Successful Defense rate (higher is better)
        - Bubble size = number of trials
        - Color = model
        - Shape = condition
        
        **What to look for:**
        - Top-left quadrant = best (high defense, low adoption)
        - Bottom-right quadrant = worst (low defense, high adoption)
        - Which model-condition pairs are in top-left?
        """)
    
    st.divider()
    
    st.subheader("Condition Effects Tab Diagrams")
    
    with st.expander("Hallucination Rate by Model × Condition (95% CI)"):
        st.markdown("""
        **What it shows:** Grouped bar chart with confidence intervals by condition
        
        **How to read it:**
        - Groups = models
        - Bars within group = conditions (DEFAULT, DETERMINISTIC, SAFETY_INSTRUCTION)
        - Error bars = 95% confidence intervals
        - Color = condition
        
        **What to look for:**
        - Which condition reduces hallucinations most?
        - Do safety instructions help?
        - Does deterministic prompting help?
        - Are effects consistent across models?
        """)
    
    with st.expander("Outcome Mix by Condition"):
        st.markdown("""
        **What it shows:** Stacked bar chart of outcomes by condition
        
        **How to read it:**
        - Each bar = one condition
        - Segments = outcome categories
        - Height = percentage
        
        **What to look for:**
        - Which condition has highest Successful Defense?
        - Which condition has lowest Silent Adoption?
        - How do conditions affect outcome distribution?
        """)
    
    with st.expander("Hallucination Rate Heatmap (Model × Condition)"):
        st.markdown("""
        **What it shows:** Heatmap of hallucination rates by model and condition
        
        **How to read it:**
        - Cells = model-condition combinations
        - Color = hallucination rate (green = low, red = high)
        - Darker color = higher rate
        
        **What to look for:**
        - Which cells are green (good performance)?
        - Which cells are red (poor performance)?
        - Patterns across conditions
        - Patterns across models
        """)
    
    st.divider()
    
    st.subheader("Length Effects Tab Diagrams")
    
    with st.expander("Short vs Long Vignette (95% CI)"):
        st.markdown("""
        **What it shows:** Line chart comparing hallucination rates by vignette length
        
        **How to read it:**
        - Lines = model-condition combinations
        - X-axis = vignette length (Short, Long)
        - Y-axis = hallucination rate
        - Error bars = 95% confidence intervals
        - Line style = condition
        
        **What to look for:**
        - Does hallucination rate change with length?
        - Which length is better for each model?
        - Are effects consistent across conditions?
        - Do confidence intervals overlap?
        """)
    
    with st.expander("Risk Difference: Short − Long"):
        st.markdown("""
        **What it shows:** Bar chart of risk difference between short and long vignettes
        
        **How to read it:**
        - Bars = model-condition combinations
        - Height = risk difference (short rate - long rate)
        - Positive = more hallucinations in short
        - Negative = more hallucinations in long
        - Zero line = no difference
        
        **What to look for:**
        - Which direction is the effect?
        - Is the effect statistically significant (Sig. column)?
        - Magnitude of effect
        - Consistency across models
        """)
    
    with st.expander("Silent Adoption by Vignette Length"):
        st.markdown("""
        **What it shows:** Stacked bar chart of outcomes by vignette length
        
        **How to read it:**
        - Bars = vignette lengths (short, long)
        - Segments = outcome categories
        - Height = percentage
        
        **What to look for:**
        - Does length affect Silent Adoption rate?
        - Which length has better outcome distribution?
        - Are patterns consistent across models?
        """)
    
    st.divider()
    
    st.subheader("Token Analysis Tab Diagrams")
    
    with st.expander("Outcomes by Fabricated Token Category"):
        st.markdown("""
        **What it shows:** Stacked bar chart of outcomes by token category
        
        **How to read it:**
        - Bars = token categories (Pathway of care, Lab markers, Drugs, Assessment)
        - Segments = outcome categories
        - Height = percentage
        
        **What to look for:**
        - Which token categories are hardest?
        - Which categories have highest Silent Adoption?
        - Are certain categories consistently problematic?
        - Model-specific weaknesses
        """)
    
    with st.expander("Silent Adoption Rate by Token Category"):
        st.markdown("""
        **What it shows:** Bar chart of adoption failure by token category
        
        **How to read it:**
        - Bars = token categories
        - Height = adoption failure rate
        - Higher = worse (more hallucination)
        
        **What to look for:**
        - Which categories have highest adoption rates?
        - Which categories are safest?
        - Relative difficulty of categories
        """)
    
    with st.expander("Detection Success by Token Category"):
        st.markdown("""
        **What it shows:** Bar chart of detection success by token category
        
        **How to read it:**
        - Bars = token categories
        - Height = detection success rate
        - Higher = better (more detection)
        
        **What to look for:**
        - Which categories have highest detection?
        - Which categories are hardest to detect?
        - Model strengths by category
        """)
    
    st.divider()
    
    st.subheader("Case Explorer Tab Diagrams")
    
    with st.expander("Per-Case Outcome Heatmap"):
        st.markdown("""
        **What it shows:** Heatmap showing outcomes for each case across models
        
        **How to read it:**
        - Rows = individual cases
        - Columns = models
        - Cell color = outcome category
        - Green = Successful Defense, Red = Silent Adoption
        
        **What to look for:**
        - Which cases are hardest (mostly red)?
        - Which cases are easiest (mostly green)?
        - Are there cases where all models fail?
        - Are there cases where all models succeed?
        - Model-specific difficult cases
        """)
    
    with st.expander("Cases Where All Models Failed/Succeeded"):
        st.markdown("""
        **What it shows:** Lists of cases with universal outcomes
        
        **How to read it:**
        - Failed cases = all models showed Silent Adoption
        - Succeeded cases = all models showed Successful Defense
        
        **What to look for:**
        - What makes failed cases so difficult?
        - What makes succeeded cases so easy?
        - Patterns in case characteristics
        - Implications for model improvement
        """)
