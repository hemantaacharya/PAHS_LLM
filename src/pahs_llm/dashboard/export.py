"""
Dashboard Export Utilities
PDF reports, publication-ready figures, and data exports
"""
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go


def generate_publication_report(
    df: pd.DataFrame,
    leaderboard: pd.DataFrame,
    run_summary: Optional[Dict],
    output_format: str = "markdown"
) -> str:
    """
    Generate a publication-ready report in markdown or LaTeX format.
    
    Args:
        df: Filtered trial data
        leaderboard: Model leaderboard data
        run_summary: Study run summary
        output_format: "markdown" or "latex"
        
    Returns:
        Formatted report string
    """
    if output_format == "markdown":
        report = []
        report.append("# PAHS LLM Hallucination Study Results\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        report.append(f"**Total trials:** {len(df):,}\n")
        report.append(f"**Models:** {df['model_full'].nunique()}\n\n")
        
        report.append("## Model Performance Summary\n")
        report.append("| Model | Defense Rate | Adoption Rate | Dangerous Reasoning |\n")
        report.append("|-------|--------------|---------------|---------------------|\n")
        
        for _, row in leaderboard.iterrows():
            report.append(
                f"| {row['model_label']} | "
                f"{row['successful_defense_rate']*100:.1f}% | "
                f"{row['silent_adoption_rate']*100:.1f}% | "
                f"{row['dangerous_reasoning_hallucination_rate']*100:.1f}% |\n"
            )
        
        return "".join(report)
    
    return ""


def create_download_button(
    data: str,
    filename: str,
    label: str,
    mime_type: str = "text/plain"
) -> None:
    """
    Create a Streamlit download button for data export.
    
    Args:
        data: String data to download
        filename: Suggested filename
        label: Button label
        mime_type: MIME type for download
    """
    import streamlit as st
    
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)


def export_figure(fig: go.Figure, filename: str, formats: List[str] = ["png", "svg"]) -> Dict[str, bytes]:
    """
    Export Plotly figure to multiple formats.
    
    Args:
        fig: Plotly figure
        filename: Base filename (without extension)
        formats: List of formats to export
        
    Returns:
        Dictionary of format -> bytes
    """
    exports = {}
    
    for fmt in formats:
        if fmt == "png":
            exports["png"] = fig.to_image(format="png", width=800, height=500, scale=2)
        elif fmt == "svg":
            exports["svg"] = fig.to_image(format="svg")
        elif fmt == "pdf":
            exports["pdf"] = fig.to_image(format="pdf")
    
    return exports


def create_figure_download_package(figures: Dict[str, go.Figure]) -> str:
    """
    Create a JSON manifest for all exported figures.
    
    Args:
        figures: Dictionary of name -> figure
        
    Returns:
        JSON string with figure metadata
    """
    manifest = {
        "generated": datetime.now().isoformat(),
        "figures": {
            name: {
                "title": fig.layout.title.text if fig.layout.title else name,
                "formats": ["png", "svg"],
            }
            for name, fig in figures.items()
        }
    }
    return json.dumps(manifest, indent=2)