"""Generate the HTML report locally by calling functions in `main.py`.
Placed in `scripts/` and writes generated artifacts to `outputs/reports/`.
"""
from pathlib import Path
import pandas as pd
import importlib.util
import sys

# Ensure project root is on sys.path so local packages (app/) can be imported
sys.path.insert(0, str(Path('.').resolve()))
spec = importlib.util.spec_from_file_location("insight_main", Path("main.py").resolve())
insight_main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = insight_main
spec.loader.exec_module(insight_main)

SAMPLE = Path("examples/sample.csv")
OUT = Path("outputs/reports/last_report_local.html")

if not SAMPLE.exists():
    print("sample not found", SAMPLE)
    raise SystemExit(2)

df = pd.read_csv(SAMPLE)
summary = insight_main._analyze_dataframe(df, missingness_threshold=0.5)
# Use the app.reporting-based visualizations now exposed by main
try:
    images = insight_main._make_visualizations(df)
except AttributeError:
    # Fallback: try to use the app.reporting helpers directly
    images = []
    numeric = list(df.select_dtypes(include=["number"]).columns)
    if numeric:
        col = numeric[0]
        series = df[col].dropna()
        if not series.empty:
            fig1 = insight_main.plot_histogram(series, title=f"Histogram — {col}")
            images.append(insight_main._fig_to_base64(fig1))

html = insight_main._build_html_report(summary, images=images)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT)
