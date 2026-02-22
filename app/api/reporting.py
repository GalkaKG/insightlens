"""Reporting utilities for InsightLens.

This module provides helpers to produce self-contained HTML reports with
embedded matplotlib plots and compact JSON summaries suitable for the
student project. Templates are provided as a minimal Jinja2 scaffold that
can be extended.

Example usage::

    html = render_html_report(summary, figures)
    json_obj = build_json_report(summary)

"""

from __future__ import annotations

import base64
import io
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template


DEFAULT_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>InsightLens Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; }
      h1 { font-size: 1.5rem; }
      .section { margin-top: 1rem; }
      .plot { margin: 0.5rem 0; }
      table { border-collapse: collapse; }
      td, th { border: 1px solid #ddd; padding: 6px 8px; }
    </style>
  </head>
  <body>
    <h1>{{ title }}</h1>
    <div class="section">
      <h2>Summary</h2>
      <ul>
        <li>Rows: {{ summary.n_rows }}</li>
        <li>Columns: {{ summary.n_columns }}</li>
      </ul>
    </div>
    <div class="section">
      <h2>Column types</h2>
      <table>
        <thead><tr><th>Column</th><th>Type</th></tr></thead>
        <tbody>
        {% for col, dtype in summary.dtypes.items() %}
          <tr><td>{{ col }}</td><td>{{ dtype }}</td></tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
    <div class="section">
      <h2>Plots</h2>
      {% for fig in figures %}
        <div class="plot"><img src="data:image/png;base64,{{ fig }}" alt="plot"/></div>
      {% endfor %}
    </div>
  </body>
</html>
"""


def fig_to_base64(fig: plt.Figure, fmt: str = "png") -> str:
    """Convert a matplotlib Figure to a base64-encoded data URL fragment.

    Returns the base64 string (without the data: prefix) suitable for
    embedding in an `img` tag as `src="data:image/png;base64,{...}"`.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, bbox_inches="tight")
    buf.seek(0)
    b = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return b


def plot_histogram(series: pd.Series, bins: int = 30, title: Optional[str] = None) -> plt.Figure:
    """Create a histogram figure for a numeric series."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(series.dropna(), bins=bins, color="#337ab7", edgecolor="#ffffff")
    ax.set_title(title or "Histogram")
    ax.set_ylabel("count")
    ax.set_xlabel(series.name or "")
    plt.tight_layout()
    return fig


def plot_boxplot(series: pd.Series, title: Optional[str] = None) -> plt.Figure:
    """Create a boxplot figure for a numeric series."""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.boxplot(series.dropna(), vert=False)
    ax.set_title(title or "Boxplot")
    plt.tight_layout()
    return fig


def build_json_report(summary: Dict) -> Dict:
    """Return a compact JSON-serializable report from the analysis summary."""
    # Here we assume `summary` is already JSON-serializable (dicts, lists, primitives)
    return {"report": summary}


def render_html_report(summary: Dict, figures: Optional[List[str]] = None, template: Optional[Template] = None) -> str:
    """Render an HTML report using the provided Jinja2 template or the default.

    `figures` should be a list of base64 image strings (as produced by
    `fig_to_base64`).
    """
    if template is None:
        env = Environment()
        template = env.from_string(DEFAULT_TEMPLATE)
    ctx = {
        "title": "InsightLens Report",
        "summary": summary,
        "figures": figures or [],
    }
    return template.render(**ctx)


__all__ = [
    "fig_to_base64",
    "plot_histogram",
    "plot_boxplot",
    "build_json_report",
    "render_html_report",
]
