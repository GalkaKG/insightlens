"""Generate the HTML report locally by calling functions in `main.py`.
This avoids relying on the running server reload state.
"""
from pathlib import Path
import pandas as pd
import importlib.util
import sys

# Load main.py as a module regardless of sys.path
# Ensure project root is on sys.path so local packages (app/) can be imported
sys.path.insert(0, str(Path('.').resolve()))
spec = importlib.util.spec_from_file_location("insight_main", Path("main.py").resolve())
insight_main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = insight_main
spec.loader.exec_module(insight_main)

SAMPLE = Path("examples/sample.csv")
OUT = Path("tools/last_report_local.html")

if not SAMPLE.exists():
    print("sample not found", SAMPLE)
    raise SystemExit(2)

df = pd.read_csv(SAMPLE)
summary = insight_main._analyze_dataframe(df, missingness_threshold=0.5)
images = insight_main._make_visualizations(df)
html = insight_main._build_html_report(summary, images=images)
OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT)
