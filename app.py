from __future__ import annotations

import io
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field


app = FastAPI(title="InsightLens (student project)")

# In-memory stores for uploaded files and generated reports.
# For a small individual project these are sufficient and simple to inspect.
_UPLOAD_STORE: Dict[str, Path] = {}
_REPORT_STORE: Dict[str, Dict[str, str]] = {}


class UploadResponse(BaseModel):
    """Response returned after a successful file upload."""

    upload_id: str = Field(..., description="Identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")


class AnalyzeRequest(BaseModel):
    """Request model for triggering analysis on an uploaded file."""

    upload_id: str = Field(..., description="Identifier returned by /upload")
    missingness_threshold: float = Field(
        0.5, description="Column missingness threshold (0-1) to flag columns"
    )


class AnalyzeResponse(BaseModel):
    """Response returned after analysis is scheduled/completed."""

    report_id: str = Field(..., description="Identifier for the generated report")
    summary: Dict[str, object] = Field(..., description="Short JSON summary of findings")


def _save_upload_file_temp(upload_file: UploadFile) -> Path:
    """Save an uploaded FastAPI UploadFile to a temporary file and return its Path.

    The temp file is created with delete=False so it persists for analysis steps.
    The caller is responsible for cleanup if long-term storage is not desired.
    """
    suffix = Path(upload_file.filename).suffix or ""
    tmp = tempfile.NamedTemporaryFile(prefix="insightlens_", suffix=suffix, delete=False)
    try:
        # Ensure we write bytes; UploadFile.file is a binary file-like object.
        shutil.copyfileobj(upload_file.file, tmp)
    finally:
        tmp.close()
        upload_file.file.close()
    return Path(tmp.name)


def _read_table(path: Path, nrows: Optional[int] = None) -> pd.DataFrame:
    """Read CSV or single-sheet Excel into a pandas DataFrame.

    Raises HTTPException(400) for unsupported formats or parsing errors.
    """
    try:
        if path.suffix.lower() in {".xls", ".xlsx"}:
            df = pd.read_excel(path, nrows=nrows)
        elif path.suffix.lower() in {".csv", ""}:
            df = pd.read_csv(path, nrows=nrows)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as exc:  # pragma: no cover - surface errors to client
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}")
    return df


def _analyze_dataframe(df: pd.DataFrame, missingness_threshold: float = 0.5) -> Dict:
    """Perform a compact EDA and validation pass on a DataFrame.

    Returns a JSON-serializable dict with descriptive statistics, missingness,
    inferred dtypes, duplicate counts, and simple IQR outlier summaries for numeric columns.
    """
    result: Dict = {}
    result["n_rows"] = int(df.shape[0])
    result["n_columns"] = int(df.shape[1])

    # Basic types and missingness
    result["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing = df.isna().sum()
    result["missingness"] = {col: int(count) for col, count in missing.items()}

    # Flag columns exceeding missingness threshold
    if df.shape[0] > 0:
        missing_frac = (missing / df.shape[0]).to_dict()
        result["missing_flags"] = {k: v for k, v in missing_frac.items() if v >= missingness_threshold}
    else:
        result["missing_flags"] = {}

    # Duplicates
    try:
        dup_count = int(df.duplicated().sum())
    except Exception:
        dup_count = 0
    result["duplicate_count"] = dup_count

    # Simple IQR outlier detection for numeric columns
    outliers: Dict[str, Dict[str, int]] = {}
    numeric = df.select_dtypes(include=["number"]).columns
    for col in numeric:
        series = df[col].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        n_out = int(((series < lower) | (series > upper)).sum())
        outliers[col] = {"outlier_count": n_out, "lower": float(lower), "upper": float(upper)}
    result["outliers"] = outliers

    # Descriptive statistics (numeric only) as compact dict
    try:
        desc = df.describe(include="number").to_dict()
    except Exception:
        desc = {}
    result["descriptive_stats"] = desc

    return result


def _build_html_report(summary: Dict) -> str:
    """Construct a minimal, self-contained HTML report from the analysis summary.

    The report is intentionally simple so it is readable and suitable for a student project.
    """
    title = "InsightLens Report"
    rows = []
    rows.append(f"<h1>{title}</h1>")
    rows.append(f"<p>Rows: {summary.get('n_rows', 0)} — Columns: {summary.get('n_columns', 0)}</p>")

    # Dtypes
    rows.append("<h2>Column types</h2>")
    rows.append("<ul>")
    for col, dt in summary.get("dtypes", {}).items():
        rows.append(f"<li><strong>{col}</strong>: {dt}</li>")
    rows.append("</ul>")

    # Missingness
    rows.append("<h2>Missingness</h2>")
    rows.append("<ul>")
    for col, count in summary.get("missingness", {}).items():
        rows.append(f"<li>{col}: {count} missing</li>")
    rows.append("</ul>")

    # Duplicates
    rows.append("<h2>Duplicates</h2>")
    rows.append(f"<p>Duplicate rows: {summary.get('duplicate_count', 0)}</p>")

    # Outliers
    rows.append("<h2>Outliers (IQR rule)</h2>")
    if summary.get("outliers"):
        rows.append("<ul>")
        for col, info in summary["outliers"].items():
            rows.append(
                f"<li>{col}: {info['outlier_count']} outliers (lower={info['lower']:.3f}, upper={info['upper']:.3f})</li>"
            )
        rows.append("</ul>")
    else:
        rows.append("<p>No numeric outliers detected or no numeric columns.</p>")

    return "\n".join(rows)


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """Endpoint to upload a CSV or single-sheet Excel file.

    Returns an `upload_id` which may be supplied to `/analyze` to trigger analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Save to temp file and record mapping
    tmp_path = _save_upload_file_temp(file)
    upload_id = uuid.uuid4().hex
    _UPLOAD_STORE[upload_id] = tmp_path
    return UploadResponse(upload_id=upload_id, filename=file.filename)


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Trigger EDA and validation for a previously uploaded file identified by `upload_id`.

    The endpoint performs analysis synchronously and returns a short JSON summary and a `report_id`.
    Reports are stored in-memory and retrievable via `/report/{report_id}`.
    """
    upload_id = req.upload_id
    if upload_id not in _UPLOAD_STORE:
        raise HTTPException(status_code=404, detail="upload_id not found")

    path = _UPLOAD_STORE[upload_id]
    df = _read_table(path)
    summary = _analyze_dataframe(df, missingness_threshold=req.missingness_threshold)

    # Build HTML and JSON artifacts
    html = _build_html_report(summary)
    report_id = uuid.uuid4().hex
    _REPORT_STORE[report_id] = {"html": html, "json": json.dumps(summary)}

    return AnalyzeResponse(report_id=report_id, summary=summary)


@app.get("/report/{report_id}")
async def get_report(report_id: str, format: str = Query("html", regex="^(html|json)$")):
    """Retrieve the generated report by `report_id`.

    Query parameter `format` selects `html` or `json` output.
    """
    if report_id not in _REPORT_STORE:
        raise HTTPException(status_code=404, detail="report_id not found")
    entry = _REPORT_STORE[report_id]
    if format == "html":
        return HTMLResponse(content=entry["html"], status_code=200)
    else:
        return JSONResponse(content=json.loads(entry["json"]), status_code=200)


@app.get("/status")
async def status() -> PlainTextResponse:
    """Lightweight health endpoint for local development."""
    return PlainTextResponse(content="InsightLens API OK", status_code=200)


__all__ = ["app"]
