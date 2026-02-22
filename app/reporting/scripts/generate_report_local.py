"""Generate the HTML report locally by calling the app's analysis + reporting helpers.

This writes the generated HTML to `app/reporting/reports/last_report_local.html`.
"""
from pathlib import Path
import pandas as pd
import importlib.util
import sys

# Ensure project root is on sys.path so local packages can be imported
sys.path.insert(0, str(Path('.').resolve()))

# Load main module to reuse the analysis routine
spec = importlib.util.spec_from_file_location("insight_main", Path("main.py").resolve())
insight_main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = insight_main
spec.loader.exec_module(insight_main)

SAMPLE = Path("examples/sample.csv")
OUT = Path("outputs/last_report_local.html")
OUT.parent.mkdir(parents=True, exist_ok=True)

if not SAMPLE.exists():
    print("sample not found", SAMPLE)
    raise SystemExit(2)

df = pd.read_csv(SAMPLE)
summary = insight_main._analyze_dataframe(df, missingness_threshold=0.5)

# Use app.reporting helpers via the facade if available
try:
    from app.reporting import plot_histogram, plot_boxplot, fig_to_base64, render_html_report
except Exception:
    # Fallback to main's embedded helpers if the facade isn't present
    plot_histogram = getattr(insight_main, "plot_histogram", None)
    plot_boxplot = getattr(insight_main, "plot_boxplot", None)
    fig_to_base64 = getattr(insight_main, "_fig_to_base64", None)
    render_html_report = getattr(insight_main, "_build_html_report", None)

figures = []
numeric = list(df.select_dtypes(include=["number"]).columns)
if numeric:
    col = numeric[0]
    series = df[col].dropna()
    if not series.empty and plot_histogram and fig_to_base64:
        fig1 = plot_histogram(series, title=f"Histogram — {col}")
        figures.append(fig_to_base64(fig1))
    if not series.empty and plot_boxplot and fig_to_base64:
        fig2 = plot_boxplot(series, title=f"Boxplot — {col}")
        figures.append(fig_to_base64(fig2))

if render_html_report:
    html = render_html_report(summary, figures=figures)
else:
    # Last-resort simple renderer
    html = "<html><body><h1>InsightLens Report</h1><pre>" + str(summary) + "</pre></body></html>"

OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT)
