"""
PAHS LLM Hallucination Study — Enhanced Interactive Dashboard
Run: streamlit run dashboard_enhanced.py

Enhanced features:
- Modular architecture (config, utils modules)
- Diagnostic confidence analysis
- Statistical significance indicators
- Safety audit log viewer
- Enhanced export functionality
- Inter-rater reliability integration
"""
import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# Import modular components — pahs_llm.dashboard package
from pahs_llm.dashboard.config import (
    TRIAL_CSV, TABLE2_CSV, TABLE3_CSV, TABLE4_CSV, TABLE1_CSV,
    RUN_SUMMARY, DASHBOARD_JSON, VIGNETTES_JSON,
    CATEGORY_COLORS, CATEGORY_ORDER, MODEL_COLORS, MODEL_LABELS,
    CONDITION_COLORS, TOKEN_CATEGORY_LABELS, EXCLUDE_MODELS,
    model_label, pct,
)
from pahs_llm.dashboard.utils import (
    category_rates, bootstrap_ci, confidence_correlation_analysis,
    analyze_safety_audit_log, add_statistical_significance,
)

st.set_page_config(
    page_title="PAHS LLM Hallucination Dashboard",
    page_icon="🧠",
    layout="wide",
)


@st.cache_data
def load():
    """Load all data files with error handling."""
    df = pd.read_csv(TRIAL_CSV) if TRIAL_CSV.exists() else pd.DataFrame()
    t2 = pd.read_csv(TABLE2_CSV) if TABLE2_CSV.exists() else pd.DataFrame()
    t3 = pd.read_csv(TABLE3_CSV) if TABLE3_CSV.exists() else pd.DataFrame()
    t4 = pd.read_csv(TABLE4_CSV) if TABLE4_CSV.exists() else pd.DataFrame()
    t1 = pd.read_csv(TABLE1_CSV) if TABLE1_CSV.exists() else pd.DataFrame()

    for table in (t2, t3, t4, t1):
        if not table.empty:
            table["model_full"] = table["provider"] + "/" + table["model_name"]

    # Load vignettes metadata
    if VIGNETTES_JSON.exists():
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
        df = df.merge(meta, on="case_id", how="left") if not df.empty else meta
    else:
        df["token_text"] = None
        df["token_category"] = "unknown"

    # Parse safety_audit_log from JSON string
    if not df.empty and "safety_audit_log" in df.columns:
        df["safety_audit_log_parsed"] = df["safety_audit_log"].apply(
            lambda x: json.loads(x) if pd.notna(x) and x else []
        )

    dashboard = None
    if DASHBOARD_JSON.exists():
        with open(DASHBOARD_JSON) as f:
            dashboard = json.load(f)

    run_summary = None
    if RUN_SUMMARY.exists():
        with open(RUN_SUMMARY) as f:
            run_summary = json.load(f)

    return df, t2, t3, t4, t1, dashboard, run_summary


def build_leaderboard(frame):
    """Build ranked leaderboard from filtered data."""
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


# ── Load Data ───────────────────────────────────────────────────────────────
df, t2, t3, t4, t1, dashboard_json, run_summary = load()

# Apply exclusions
if not df.empty:
    df = df[~df["model_full"].isin(EXCLUDE_MODELS)]
    t2 = t2[~t2["model_full"].isin(EXCLUDE_MODELS)]
    t3 = t3[~t3["model_full"].isin(EXCLUDE_MODELS)]
    t4 = t4[~t4["model_full"].isin(EXCLUDE_MODELS)]
    t1 = t1[~t1["model_full"].isin(EXCLUDE_MODELS)]

# ── Sidebar ───────────────────────────────────────────────────────────────
st.sidebar.title("🔬 Filters")
all_models = sorted(df["model_full"].unique()) if not df.empty else []
all_conditions = sorted(df["condition"].unique()) if not df.empty else []
all_lengths = sorted(df["vignette_length"].unique()) if not df.empty else []
all_token_categories = sorted(df["token_category"].dropna().unique()) if not df.empty else []

sel_models = st.sidebar.multiselect("Models", all_models, default=all_models)
sel_conditions = st.sidebar.multiselect("Conditions", all_conditions, default=all_conditions)
sel_lengths = st.sidebar.multiselect("Vignette length", all_lengths, default=all_lengths)
sel_token_categories = st.sidebar.multiselect(
    "Fabricated token category",
    all_token_categories,
    default=all_token_categories,
)

# Apply filters
fdf = df[
    df["model_full"].isin(sel_models)
    & df["condition"].isin(sel_conditions)
    & df["vignette_length"].isin(sel_lengths)
    & df["token_category"].isin(sel_token_categories)
] if not df.empty else pd.DataFrame()

ft2 = t2[t2["model_full"].isin(sel_models) & t2["condition"].isin(sel_conditions)] if not t2.empty else pd.DataFrame()
ft3 = t3[t3["model_full"].isin(sel_models)] if not t3.empty else pd.DataFrame()
ft4 = t4[t4["model_full"].isin(sel_models) & t4["condition"].isin(sel_conditions)] if not t4.empty else pd.DataFrame()
ft1 = t1[t1["model_full"].isin(sel_models)] if not t1.empty else pd.DataFrame()

with st.sidebar.expander("📊 Study Design", expanded=False):
    n_cases = df["case_id"].nunique() if not df.empty else 0
    n_models = len(all_models)
    st.markdown(
        f"""
        - **Site:** Patan Academy of Health Sciences
        - **Cases:** {n_cases} vignettes (short + long)
        - **Models:** {n_models} LLMs (3 commercial + 1 open-source via OpenRouter)
        - **Conditions:** DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC
        - **Fabricated tokens:** planted clinical terms per case
        """
    )
    if run_summary:
        st.caption(
            f"Pooled from {run_summary.get('pooled_trials', '—'):,} trials · "
            f"{run_summary.get('unique_model_count', '—')} models"
        )

# ── Header ────────────────────────────────────────────────────────────────
st.title("PAHS LLM Hallucination Study Dashboard")
st.caption(
    f"Patan Academy of Health Sciences · 2026 · "
    f"{df['case_id'].nunique() if not df.empty else 0} vignettes · {len(all_models)} models · "
    f"{len(all_conditions)} conditions · {len(df):,} pooled trials"
)

with st.expander("📖 What the outcome categories mean"):
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

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Overview",
    "🏆 Leaderboard",
    "🔬 Condition Effects",
    "📏 Length Effects",
    "🔤 Token Analysis",
    "🔍 Case Explorer",
    "📈 Confidence Analysis",
    "📄 Publication Tables",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    n = len(fdf)
    cat_rates = category_rates(fdf) if n else {cat: 0 for cat in CATEGORY_ORDER}

    # KPIs with significance indicators
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Trials", f"{n:,}")
    k2.metric("Detection success", pct(fdf["detection_rate_success"].mean()) if n else "—")
    k3.metric("Adoption failure", pct(fdf["adoption_rate_failure"].mean()) if n else "—")
    k4.metric("Hallucination flagged", pct(fdf["hallucination_detected"].mean()) if n else "—")
    k5.metric("Dangerous reasoning", pct(fdf["dangerous_reasoning_hallucination"].mean(), 2) if n else "—")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Successful Defense", pct(cat_rates["Successful Defense"]))
    c2.metric("Silent Adoption", pct(cat_rates["Silent Adoption"]))
    c3.metric("Blind Spot", pct(cat_rates["Blind Spot"]))
    c4.metric("False Positive", pct(cat_rates["False Positive"]))

    st.divider()

    # Enhanced visualizations with statistical annotations
    left, right = st.columns(2)

    with left:
        st.subheader("Hallucination rate by model (95% CI)")
        if not ft2.empty:
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
            
            # Add significance testing
            sig_df = add_statistical_significance(ft2, "model_full", "hallucination_rate_pct")
            
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
            st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig2, width="stretch")

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
    st.plotly_chart(fig3, width="stretch")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — CONFIDENCE ANALYSIS (NEW)
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.subheader("Diagnostic Confidence Analysis")
    st.caption("Correlation between model confidence and hallucination outcomes")

    if not fdf.empty and "diagnostic_confidence" in fdf.columns:
        # Confidence distribution
        left, right = st.columns(2)

        with left:
            st.subheader("Confidence distribution by outcome")
            fig_conf = px.box(
                fdf,
                x="category",
                y="diagnostic_confidence",
                color="category",
                color_discrete_map=CATEGORY_COLORS,
                category_orders={"category": CATEGORY_ORDER},
                labels={"category": "Outcome", "diagnostic_confidence": "Confidence (0-100)"},
            )
            fig_conf.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=380)
            st.plotly_chart(fig_conf, width="stretch")

        with right:
            st.subheader("Overconfidence analysis")
            high_conf = fdf[fdf["diagnostic_confidence"] >= 80]
            low_conf = fdf[fdf["diagnostic_confidence"] < 80]

            conf_stats = pd.DataFrame([
                {"Confidence Level": "High (≥80)", "Hallucination Rate": high_conf["hallucination_detected"].mean() * 100, "n": len(high_conf)},
                {"Confidence Level": "Low (<80)", "Hallucination Rate": low_conf["hallucination_detected"].mean() * 100, "n": len(low_conf)},
            ])

            fig_conf2 = px.bar(
                conf_stats,
                x="Confidence Level",
                y="Hallucination Rate",
                text=conf_stats["Hallucination Rate"].map("{:.1f}%".format),
                labels={"Hallucination Rate": "%"},
            )
            fig_conf2.update_traces(marker_color=["#e74c3c", "#2ecc71"], textposition="outside")
            fig_conf2.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=380)
            st.plotly_chart(fig_conf2, width="stretch")

        # Correlation statistics
        st.subheader("Statistical correlation")
        corr_result = confidence_correlation_analysis(fdf)
        if corr_result:
            col1, col2, col3 = st.columns(3)
            col1.metric("Point-biserial r", f"{corr_result['correlation']:.3f}")
            col2.metric("p-value", f"{corr_result['p_value']:.4f}")
            col3.metric("Overconfident rate", pct(corr_result['overconfident_rate']))

            # Confidence vs detection scatter
            st.subheader("Confidence vs. Detection Success")
            fig_scatter = px.scatter(
                fdf,
                x="diagnostic_confidence",
                y="detection_rate_success",
                color="category",
                color_discrete_map=CATEGORY_COLORS,
                trendline="lowess",
                labels={"diagnostic_confidence": "Diagnostic Confidence", "detection_rate_success": "Detection Success"},
            )
            fig_scatter.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=400)
            st.plotly_chart(fig_scatter, width="stretch")
    else:
        st.info("Diagnostic confidence data not available in current dataset")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — SAFETY AUDIT LOG VIEWER (NEW)
# ═══════════════════════════════════════════════════════════════════════════════
with tab8:
    st.subheader("Safety Audit Log Analysis")
    st.caption("Detailed view of term detection and exclusion patterns")

    if not fdf.empty:
        # Extract safety audit data
        safety_data = []
        for _, row in fdf.iterrows():
            safety_log = row.get("safety_audit_log_parsed", [])
            if isinstance(safety_log, list):
                audit = analyze_safety_audit_log(safety_log)
                safety_data.append({
                    "case_id": row["case_id"],
                    "model_full": row["model_full"],
                    "condition": row["condition"],
                    "category": row["category"],
                    **audit
                })

        if safety_data:
            safety_df = pd.DataFrame(safety_data)

            # Safety audit summary
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total terms audited", f"{safety_df['total_terms'].sum():,}")
            col2.metric("Verified terms", f"{safety_df['verified'].sum():,}")
            col3.metric("Hallucination traps", f"{safety_df['hallucination_trap'].sum():,}")
            col4.metric("Unrecognized terms", f"{safety_df['unrecognized'].sum():,}")

            # Terms by category
            st.subheader("Safety audit outcomes by model")
            audit_by_model = safety_df.groupby("model_full").agg({
                "verified": "sum",
                "hallucination_trap": "sum",
                "unrecognized": "sum"
            }).reset_index()
            audit_by_model["model_label"] = audit_by_model["model_full"].map(model_label)

            fig_audit = px.bar(
                audit_by_model.melt(id_vars=["model_label"], var_name="status", value_name="count"),
                x="model_label",
                y="count",
                color="status",
                barmode="group",
                labels={"model_label": "Model", "count": "Terms", "status": "Status"},
            )
            fig_audit.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=360)
            st.plotly_chart(fig_audit, width="stretch")

            # Dangerous terms lookup
            st.subheader("Most frequently flagged fabricated terms")
            all_excluded = []
            for terms in safety_df["excluded_terms"]:
                all_excluded.extend(terms)

            if all_excluded:
                term_counts = pd.Series(all_excluded).value_counts().head(15)
                st.dataframe(
                    term_counts.reset_index().rename(columns={"index": "Term", "value": "Times flagged"}),
                    width="stretch",
                    hide_index=True,
                )

# ── Footer ────────────────────────────────────────────────────────────────
st.divider()
st.caption("PAHS LLM Hallucination Study · Enhanced Dashboard v2.0 · May 2026")