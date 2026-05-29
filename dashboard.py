"""
PAHS LLM Hallucination Study — Interactive Dashboard
Run: streamlit run dashboard.py
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
TRIAL_CSV   = "04_results/analysis_ready/pooled/pooled_trial_level.csv"
TABLE2_CSV  = "04_results/analysis_ready/pooled/table2_outcomes_by_model_condition.csv"
TABLE3_CSV  = "04_results/analysis_ready/pooled/table3_condition_effects.csv"
TABLE4_CSV  = "04_results/analysis_ready/pooled/table4_length_effects.csv"
TABLE1_CSV  = "04_results/analysis_ready/pooled/table1_coverage.csv"

CATEGORY_COLORS = {
    "Blind Spot":         "#e74c3c",
    "Silent Adoption":    "#f39c12",
    "Successful Defense": "#2ecc71",
}
MODEL_COLORS = {
    "anthropic/claude-haiku-4-5":   "#9b59b6",
    "gemini/gemini-3.1-flash-lite": "#3498db",
    "openai/gpt-5.4-mini":          "#e67e22",
}
CONDITION_COLORS = {
    "DEFAULT":            "#2ecc71",
    "DETERMINISTIC":      "#3498db",
    "SAFETY_INSTRUCTION": "#e74c3c",
}

st.set_page_config(
    page_title="PAHS LLM Hallucination Dashboard",
    page_icon="🧠",
    layout="wide",
)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df   = pd.read_csv(TRIAL_CSV)
    t2   = pd.read_csv(TABLE2_CSV)
    t3   = pd.read_csv(TABLE3_CSV)
    t4   = pd.read_csv(TABLE4_CSV)
    t1   = pd.read_csv(TABLE1_CSV)
    # full model label for t2/t3/t4
    for t in [t2, t3, t4, t1]:
        t["model_full"] = t["provider"] + "/" + t["model_name"]
    return df, t2, t3, t4, t1

df, t2, t3, t4, t1 = load()

EXCLUDE = {"openai/gpt-5.5", "anthropic/claude-sonnet-4-6"}
df = df[~df["model_full"].isin(EXCLUDE)]
t2 = t2[~t2["model_full"].isin(EXCLUDE)]
t3 = t3[~t3["model_full"].isin(EXCLUDE)]
t4 = t4[~t4["model_full"].isin(EXCLUDE)]
t1 = t1[~t1["model_full"].isin(EXCLUDE)]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_models     = sorted(df["model_full"].unique())
all_conditions = sorted(df["condition"].unique())
all_lengths    = sorted(df["vignette_length"].unique())

sel_models     = st.sidebar.multiselect("Models",          all_models,     default=all_models)
sel_conditions = st.sidebar.multiselect("Conditions",      all_conditions, default=all_conditions)
sel_lengths    = st.sidebar.multiselect("Vignette length", all_lengths,    default=all_lengths)

fdf = df[
    df["model_full"].isin(sel_models) &
    df["condition"].isin(sel_conditions) &
    df["vignette_length"].isin(sel_lengths)
]
ft2 = t2[t2["model_full"].isin(sel_models) & t2["condition"].isin(sel_conditions)]
ft3 = t3[t3["model_full"].isin(sel_models)]
ft4 = t4[t4["model_full"].isin(sel_models) & t4["condition"].isin(sel_conditions)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧠 PAHS LLM Hallucination Study")
st.caption("Patan Academy of Health Sciences · 2026 · 300 psychiatry vignettes · 3 models · 3 conditions · 5,400 trials")

# ── KPIs ──────────────────────────────────────────────────────────────────────
n = len(fdf)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Trials",              f"{n:,}")
k2.metric("Hallucination rate",  f"{fdf['hallucination_detected'].mean():.1%}" if n else "—")
k3.metric("Adoption failure",    f"{fdf['adoption_rate_failure'].mean():.1%}"  if n else "—")
k4.metric("Detection success",   f"{fdf['detection_rate_success'].mean():.1%}" if n else "—")
k5.metric("Dangerous reasoning", f"{fdf['dangerous_reasoning_hallucination'].mean():.2%}" if n else "—")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "⚗️ Condition Effects",
    "📏 Length Effects",
    "🗺️ Per-Case Explorer",
    "📋 Publication Tables",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    # Hallucination rate by model with CI
    with c1:
        st.subheader("Hallucination rate by model (95% CI)")
        agg = (
            ft2.groupby("model_full")
            .apply(lambda x: pd.Series({
                "rate":    x["hallucination_rate_pct"].mean(),
                "ci_low":  x["hall_ci_low_pct"].mean(),
                "ci_high": x["hall_ci_high_pct"].mean(),
            }))
            .reset_index()
            .sort_values("rate")
        )
        fig = go.Figure()
        for _, row in agg.iterrows():
            color = MODEL_COLORS.get(row["model_full"], "#888")
            fig.add_trace(go.Bar(
                x=[row["rate"]], y=[row["model_full"]],
                orientation="h",
                marker_color=color,
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=[row["ci_high"] - row["rate"]],
                    arrayminus=[row["rate"] - row["ci_low"]],
                    color="#333", thickness=2,
                ),
                text=f"{row['rate']:.1f}%",
                textposition="outside",
                name=row["model_full"],
                showlegend=False,
            ))
        fig.update_layout(
            xaxis=dict(title="Hallucination rate (%)", range=[0, 105]),
            yaxis=dict(title=""),
            margin=dict(l=0, r=30, t=10, b=10), height=220,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Outcome category distribution
    with c2:
        st.subheader("Outcome category distribution")
        cat = fdf["category"].value_counts().reset_index()
        cat.columns = ["category", "count"]
        fig2 = px.pie(
            cat, names="category", values="count",
            color="category", color_discrete_map=CATEGORY_COLORS,
            hole=0.45,
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=260)
        st.plotly_chart(fig2, use_container_width=True)

    # Stacked category % by model
    st.subheader("Outcome categories by model (stacked %)")
    cat_model = fdf.groupby(["model_full", "category"]).size().reset_index(name="count")
    totals = cat_model.groupby("model_full")["count"].transform("sum")
    cat_model["pct"] = cat_model["count"] / totals * 100
    fig3 = px.bar(
        cat_model, x="model_full", y="pct", color="category",
        color_discrete_map=CATEGORY_COLORS,
        text=cat_model["pct"].map("{:.1f}%".format),
        labels={"model_full": "Model", "pct": "%", "category": "Outcome"},
    )
    fig3.update_traces(textposition="inside")
    fig3.update_layout(
        barmode="stack", yaxis_ticksuffix="%",
        margin=dict(l=0, r=0, t=10, b=10), height=320,
        xaxis_tickangle=0,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Endorsed vs detected hallucination
    st.subheader("Detected vs endorsed hallucination by model")
    st.caption("Endorsed = model explicitly agreed with the fabricated detail (subset of detected)")
    end_agg = (
        fdf.groupby("model_full")[["hallucination_detected", "endorsed_hallucination"]]
        .mean()
        .mul(100)
        .reset_index()
        .melt(id_vars="model_full", var_name="metric", value_name="rate")
    )
    end_agg["metric"] = end_agg["metric"].map({
        "hallucination_detected":  "Detected",
        "endorsed_hallucination":  "Endorsed",
    })
    fig4 = px.bar(
        end_agg, x="model_full", y="rate", color="metric",
        barmode="group",
        text=end_agg["rate"].map("{:.1f}%".format),
        color_discrete_map={"Detected": "#e74c3c", "Endorsed": "#c0392b"},
        labels={"model_full": "Model", "rate": "%", "metric": ""},
    )
    fig4.update_traces(textposition="outside")
    fig4.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=320, xaxis_tickangle=0)
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONDITION EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Hallucination rate by model × condition (95% CI)")
    fig5 = go.Figure()
    conditions = ["DEFAULT", "DETERMINISTIC", "SAFETY_INSTRUCTION"]
    for cond in conditions:
        sub = ft2[ft2["condition"] == cond].sort_values("model_full")
        fig5.add_trace(go.Bar(
            name=cond,
            x=sub["model_full"],
            y=sub["hallucination_rate_pct"],
            error_y=dict(
                type="data", symmetric=False,
                array=(sub["hall_ci_high_pct"] - sub["hallucination_rate_pct"]).tolist(),
                arrayminus=(sub["hallucination_rate_pct"] - sub["hall_ci_low_pct"]).tolist(),
                color="#333", thickness=1.5,
            ),
            marker_color=CONDITION_COLORS.get(cond, "#888"),
            text=sub["hallucination_rate_pct"].map("{:.1f}%".format),
            textposition="outside",
        ))
    fig5.update_layout(
        barmode="group", yaxis=dict(title="Hallucination rate (%)", range=[0, 115]),
        margin=dict(l=0, r=0, t=10, b=10), height=380, xaxis_tickangle=0,
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Risk ratio table
    st.subheader("Condition effect — Risk Ratio vs DEFAULT (95% CI)")
    st.caption("RR > 1 means the condition increases hallucination risk relative to DEFAULT")
    rr_display = ft3[["model_full", "comparison", "default_rate_pct",
                       "comparison_rate_pct", "risk_difference_pct",
                       "rd_ci_low_pct", "rd_ci_high_pct",
                       "risk_ratio", "rr_ci_low", "rr_ci_high"]].copy()
    rr_display.columns = ["Model", "Comparison", "DEFAULT %", "Comparison %",
                           "Risk Diff %", "RD CI low", "RD CI high",
                           "Risk Ratio", "RR CI low", "RR CI high"]
    rr_display["Risk Ratio"] = rr_display["Risk Ratio"].map("{:.3f}".format)
    rr_display["RR 95% CI"] = rr_display.apply(
        lambda r: f"[{r['RR CI low']:.3f}, {r['RR CI high']:.3f}]", axis=1
    )
    rr_display["RD 95% CI"] = rr_display.apply(
        lambda r: f"[{r['RD CI low']:.1f}%, {r['RD CI high']:.1f}%]", axis=1
    )
    st.dataframe(
        rr_display[["Model", "Comparison", "DEFAULT %", "Comparison %",
                    "Risk Diff %", "RD 95% CI", "Risk Ratio", "RR 95% CI"]],
        use_container_width=True, hide_index=True,
    )

    # Adoption failure by condition
    st.subheader("Adoption failure rate by model × condition")
    fig6 = px.bar(
        ft2, x="model_full", y="adoption_failure_rate_pct", color="condition",
        barmode="group",
        text=ft2["adoption_failure_rate_pct"].map("{:.1f}%".format),
        color_discrete_map=CONDITION_COLORS,
        labels={"model_full": "Model", "adoption_failure_rate_pct": "%", "condition": "Condition"},
    )
    fig6.update_traces(textposition="outside")
    fig6.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=340, xaxis_tickangle=0)
    st.plotly_chart(fig6, use_container_width=True)

    # Heatmap
    st.subheader("Hallucination rate heatmap — model × condition")
    pivot = (
        fdf.groupby(["model_full", "condition"])["hallucination_detected"]
        .mean().mul(100).unstack(fill_value=0)
    )
    fig7 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="RdYlGn_r", zmin=0, zmax=100,
        text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        colorbar=dict(title="%"),
    ))
    fig7.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=260)
    st.plotly_chart(fig7, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — LENGTH EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Short vs long vignette — hallucination rate by model × condition (95% CI)")

    fig8 = go.Figure()
    for _, row in ft4.iterrows():
        label = f"{row['model_full']} | {row['condition']}"
        fig8.add_trace(go.Scatter(
            x=["Short", "Long"],
            y=[row["short_rate_pct"], row["long_rate_pct"]],
            mode="lines+markers",
            name=label,
            line=dict(color=MODEL_COLORS.get(row["model_full"], "#888"),
                      dash="solid" if row["condition"] == "DEFAULT"
                           else "dash" if row["condition"] == "DETERMINISTIC"
                           else "dot"),
            marker=dict(size=8),
        ))
    fig8.update_layout(
        yaxis=dict(title="Hallucination rate (%)", range=[0, 105]),
        xaxis=dict(title="Vignette length"),
        margin=dict(l=0, r=0, t=10, b=10), height=400,
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Risk difference: short vs long (short − long, %)")
    st.caption("Positive = short vignettes have higher hallucination rate")
    fig9 = px.bar(
        ft4, x="model_full", y="risk_difference_pct", color="condition",
        barmode="group",
        error_y=ft4["rd_ci_high_pct"] - ft4["risk_difference_pct"],
        error_y_minus=ft4["risk_difference_pct"] - ft4["rd_ci_low_pct"],
        color_discrete_map=CONDITION_COLORS,
        text=ft4["risk_difference_pct"].map("{:+.1f}%".format),
        labels={"model_full": "Model", "risk_difference_pct": "Risk diff (%)", "condition": "Condition"},
    )
    fig9.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
    fig9.update_traces(textposition="outside")
    fig9.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=360, xaxis_tickangle=0)
    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Length effect detail table")
    len_display = ft4[["model_full", "condition", "short_n", "short_rate_pct",
                        "long_n", "long_rate_pct", "risk_difference_pct",
                        "rd_ci_low_pct", "rd_ci_high_pct",
                        "risk_ratio", "rr_ci_low", "rr_ci_high"]].copy()
    len_display["RD 95% CI"] = len_display.apply(
        lambda r: f"[{r['rd_ci_low_pct']:.1f}%, {r['rd_ci_high_pct']:.1f}%]", axis=1
    )
    len_display["RR 95% CI"] = len_display.apply(
        lambda r: f"[{r['rr_ci_low']:.3f}, {r['rr_ci_high']:.3f}]", axis=1
    )
    st.dataframe(
        len_display[["model_full", "condition", "short_n", "short_rate_pct",
                     "long_n", "long_rate_pct", "risk_difference_pct",
                     "RD 95% CI", "risk_ratio", "RR 95% CI"]].rename(columns={
            "model_full": "Model", "condition": "Condition",
            "short_n": "Short n", "short_rate_pct": "Short %",
            "long_n": "Long n", "long_rate_pct": "Long %",
            "risk_difference_pct": "Risk Diff %", "risk_ratio": "Risk Ratio",
        }),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PER-CASE EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Per-case outcome heatmap — all 300 cases × 3 models")
    st.caption("Showing DEFAULT condition, short vignettes. Color = outcome category.")

    heat_df = df[
        (df["condition"] == "DEFAULT") &
        (df["vignette_length"] == "short")
    ][["case_id", "model_full", "category"]].copy()

    cat_num = {"Successful Defense": 2, "Blind Spot": 1, "Silent Adoption": 0}
    heat_df["cat_num"] = heat_df["category"].map(cat_num)

    pivot_heat = heat_df.pivot_table(
        index="case_id", columns="model_full", values="cat_num", aggfunc="first"
    )

    # Sort cases by total difficulty (sum of cat_num ascending = hardest first)
    pivot_heat = pivot_heat.loc[pivot_heat.sum(axis=1).sort_values().index]

    colorscale = [
        [0.0,  "#f39c12"],   # Silent Adoption
        [0.5,  "#e74c3c"],   # Blind Spot
        [1.0,  "#2ecc71"],   # Successful Defense
    ]
    fig10 = go.Figure(go.Heatmap(
        z=pivot_heat.values,
        x=pivot_heat.columns.tolist(),
        y=pivot_heat.index.tolist(),
        colorscale=colorscale,
        zmin=0, zmax=2,
        colorbar=dict(
            tickvals=[0, 1, 2],
            ticktext=["Silent Adoption", "Blind Spot", "Successful Defense"],
            title="Outcome",
        ),
        showscale=True,
        hovertemplate="Case: %{y}<br>Model: %{x}<br>Outcome: %{z}<extra></extra>",
    ))
    fig10.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=10, b=10),
        yaxis=dict(showticklabels=False, title="Cases (sorted by difficulty)"),
        xaxis=dict(title=""),
    )
    st.plotly_chart(fig10, use_container_width=True)

    # Cases where all 3 models failed
    st.subheader("Cases where all 3 models failed (Silent Adoption across all models)")
    all_fail = heat_df.groupby("case_id").apply(
        lambda x: (x["category"] == "Silent Adoption").all()
    )
    failed_cases = all_fail[all_fail].index.tolist()
    st.metric("Count", len(failed_cases))
    if failed_cases:
        st.dataframe(pd.DataFrame({"case_id": failed_cases}), use_container_width=True, hide_index=True)

    # Cases where all 3 models succeeded
    st.subheader("Cases where all 3 models succeeded (Successful Defense across all models)")
    all_win = heat_df.groupby("case_id").apply(
        lambda x: (x["category"] == "Successful Defense").all()
    )
    won_cases = all_win[all_win].index.tolist()
    st.metric("Count", len(won_cases))

    # Raw data explorer
    with st.expander("🔍 Raw trial data explorer"):
        st.dataframe(
            fdf[["model_full", "condition", "vignette_length", "case_id",
                 "hallucination_detected", "endorsed_hallucination",
                 "adoption_rate_failure", "detection_rate_success",
                 "dangerous_reasoning_hallucination", "category"]],
            use_container_width=True, height=380,
        )
        st.caption(f"{len(fdf):,} rows")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PUBLICATION TABLES
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Table 1 — Trial coverage by model")
    st.dataframe(t1.drop(columns=["model_full"]), use_container_width=True, hide_index=True)
    st.download_button("⬇ Download Table 1", t1.to_csv(index=False), "table1_coverage.csv", "text/csv")

    st.divider()
    st.subheader("Table 2 — Hallucination outcomes by model × condition")
    t2_display = ft2[[
        "model_full", "condition", "n",
        "hallucination_rate_pct", "hall_ci_low_pct", "hall_ci_high_pct",
        "endorsed_hallucination_rate_pct",
        "adoption_failure_rate_pct", "detection_success_rate_pct",
        "dangerous_reasoning_rate_pct",
    ]].copy()
    t2_display["95% CI"] = t2_display.apply(
        lambda r: f"[{r['hall_ci_low_pct']:.1f}%, {r['hall_ci_high_pct']:.1f}%]", axis=1
    )
    st.dataframe(
        t2_display.drop(columns=["hall_ci_low_pct", "hall_ci_high_pct"]).rename(columns={
            "model_full": "Model", "condition": "Condition", "n": "n",
            "hallucination_rate_pct": "Hall. rate %",
            "endorsed_hallucination_rate_pct": "Endorsed %",
            "adoption_failure_rate_pct": "Adoption fail %",
            "detection_success_rate_pct": "Detection %",
            "dangerous_reasoning_rate_pct": "Dangerous %",
        }),
        use_container_width=True, hide_index=True,
    )
    st.download_button("⬇ Download Table 2", ft2.to_csv(index=False), "table2_outcomes.csv", "text/csv")

    st.divider()
    st.subheader("Table 3 — Condition effects vs DEFAULT (Risk Ratio & Risk Difference)")
    t3_display = ft3.copy()
    t3_display["RR (95% CI)"] = t3_display.apply(
        lambda r: f"{r['risk_ratio']:.3f} [{r['rr_ci_low']:.3f}, {r['rr_ci_high']:.3f}]", axis=1
    )
    t3_display["RD % (95% CI)"] = t3_display.apply(
        lambda r: f"{r['risk_difference_pct']:+.1f}% [{r['rd_ci_low_pct']:.1f}%, {r['rd_ci_high_pct']:.1f}%]", axis=1
    )
    st.dataframe(
        t3_display[["model_full", "comparison", "default_rate_pct",
                    "comparison_rate_pct", "RD % (95% CI)", "RR (95% CI)"]].rename(columns={
            "model_full": "Model", "comparison": "Comparison",
            "default_rate_pct": "DEFAULT %", "comparison_rate_pct": "Comparison %",
        }),
        use_container_width=True, hide_index=True,
    )
    st.download_button("⬇ Download Table 3", ft3.to_csv(index=False), "table3_condition_effects.csv", "text/csv")

    st.divider()
    st.subheader("Table 4 — Length effects (short vs long)")
    t4_display = ft4.copy()
    t4_display["RR (95% CI)"] = t4_display.apply(
        lambda r: f"{r['risk_ratio']:.3f} [{r['rr_ci_low']:.3f}, {r['rr_ci_high']:.3f}]", axis=1
    )
    t4_display["RD % (95% CI)"] = t4_display.apply(
        lambda r: f"{r['risk_difference_pct']:+.1f}% [{r['rd_ci_low_pct']:.1f}%, {r['rd_ci_high_pct']:.1f}%]", axis=1
    )
    st.dataframe(
        t4_display[["model_full", "condition", "short_n", "short_rate_pct",
                    "long_n", "long_rate_pct", "RD % (95% CI)", "RR (95% CI)"]].rename(columns={
            "model_full": "Model", "condition": "Condition",
            "short_n": "Short n", "short_rate_pct": "Short %",
            "long_n": "Long n", "long_rate_pct": "Long %",
        }),
        use_container_width=True, hide_index=True,
    )
    st.download_button("⬇ Download Table 4", ft4.to_csv(index=False), "table4_length_effects.csv", "text/csv")
