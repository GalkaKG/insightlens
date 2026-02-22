"""Facade package for reporting utilities.

Re-exports functions from the existing `app.api.reporting` module so callers
can use `app.reporting.*` which is clearer for project structure.
"""
from app.api.reporting import (
    fig_to_base64,
    plot_histogram,
    plot_boxplot,
    build_json_report,
    render_html_report,
)

__all__ = [
    "fig_to_base64",
    "plot_histogram",
    "plot_boxplot",
    "build_json_report",
    "render_html_report",
]
