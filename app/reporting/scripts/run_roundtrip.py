"""Developer helper: upload examples/sample.csv to local server, trigger analysis,
and save the HTML report under app/reporting/reports/.

Place this in `app/reporting/scripts/` per project layout preference.
"""
import httpx
from pathlib import Path
import sys

BASE = "http://127.0.0.1:8000"
SAMPLE = Path("examples/sample.csv")
OUT = Path("app/reporting/reports/last_report.html")

if not SAMPLE.exists():
    print("Sample file not found:", SAMPLE)
    sys.exit(2)

OUT.parent.mkdir(parents=True, exist_ok=True)

with httpx.Client(base_url=BASE, timeout=30.0) as client:
    print("Uploading", SAMPLE)
    with SAMPLE.open("rb") as fh:
        resp = client.post("/upload", files={"file": (SAMPLE.name, fh)})
    resp.raise_for_status()
    up = resp.json()
    print("Upload id:", up.get("upload_id"))

    payload = {"upload_id": up.get("upload_id"), "missingness_threshold": 0.5}
    print("Requesting analysis...")
    resp2 = client.post("/analyze", json=payload)
    resp2.raise_for_status()
    ar = resp2.json()
    print("Report id:", ar.get("report_id"))

    rid = ar.get("report_id")
    print("Fetching HTML report...")
    rpt = client.get(f"/report/{rid}?format=html")
    rpt.raise_for_status()
    html = rpt.text
    OUT.write_text(html, encoding="utf-8")
    print("Saved HTML to", OUT)

    print("Fetching JSON summary...")
    jr = client.get(f"/report/{rid}?format=json")
    jr.raise_for_status()
    print(jr.json())

print("Roundtrip complete.")
