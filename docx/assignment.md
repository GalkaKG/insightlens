# AI for Developers – January 2026 Individual Project Assignment

## Project Overview

**Introduction**

InsightLens is a FastAPI web application for automated data-quality validation and rapid exploratory data analysis (EDA) of tabular datasets. Leveraging pandas, the system produces reproducible, machine-readable validation artifacts and concise human-facing reports to accelerate trustworthy data preparation.

**Problem Statement**

Practitioners routinely ingest CSV and Excel files that contain missing values, inconsistent types, duplicates, and other latent quality issues. Manual inspection is laborious, non-reproducible, and often delayed until after model development or reporting, increasing the risk of erroneous conclusions. Automated, repeatable validation combined with EDA is required to detect and remediate problems early in the data pipeline.

**Target Users**

- Data scientists and machine-learning engineers requiring fast, reproducible EDA.
- Data analysts and BI professionals validating incoming datasets before reporting.
- Data engineers and ETL developers integrating quality checks into ingestion workflows.
- Instructors and students using a teachable tool for data-quality concepts.

**Functional Requirements**

- Accept CSV and Excel uploads (single and multi-sheet) and expose REST endpoints via FastAPI.
- Detect and report missingness patterns, type inconsistencies, duplicates, outliers, and invalid categorical values.
- Generate EDA summaries: descriptive statistics, distributions, correlation matrices, and variable-level visualizations.
- Provide configurable validation rules (thresholds, ranges, regex) and produce both human-readable (HTML/PDF) and machine-readable (JSON) reports.
- Support export of cleaned/annotated datasets and detailed validation logs.

**Non-Functional Requirements**

- Performance: handle moderate-sized datasets efficiently using pandas optimizations and memory-aware processing.
- Scalability: stateless API design to allow horizontal scaling behind load balancers.
- Reliability: deterministic checks, robust error handling, and comprehensive logging.
- Usability: concise, interpretable reports suitable for technical and non-technical stakeholders.
- Security & Privacy: input validation, size limits, and no persistent storage of sensitive data by default.

**Project Scope**

The initial deliverable implements core validators, EDA summaries, REST endpoints, and HTML/JSON reporting for CSV and Excel inputs. Future work may add distributed processing, richer visualizations, and integrations with orchestration pipelines.

## System Architecture – Modules

### API Layer

Purpose: Provide a minimal REST interface for file upload, analysis requests, and retrieval of results. The layer exposes a small set of endpoints implemented with FastAPI and uses Pydantic models for simple input validation. It is designed for local development and testing by a single student rather than for production deployment. AI assistance: GitHub Copilot suggested idiomatic route patterns, Pydantic schemas, and example tests that accelerated scaffold creation.

### Data Ingestion and Parsing

Purpose: Read uploaded CSV and single-sheet Excel files into canonical pandas DataFrames, perform size/type checks, and normalize common value encodings (e.g., whitespace trimming, missing-value markers). The module favors clarity and robustness for modest datasets (target ≈100k rows) and emits clear parsing errors for instructional debugging. AI assistance: GitHub Copilot provided robust pandas read patterns and error-handling idioms that were adapted and simplified for the student project.

### Validation Engine

Purpose: Execute a concise set of rule-based validators (missingness thresholds, type consistency, duplicate detection, and IQR-based outlier detection) and produce a structured summary of findings. Rules are configurable via a small JSON file or query parameters to keep experimentation reproducible for coursework. AI assistance: GitHub Copilot generated compact validator templates and example unit tests that reduced development time and helped ensure deterministic behavior.

### Reporting Layer

Purpose: Transform validation results and EDA summaries into a readable HTML report and a compact JSON payload; include static images of basic plots (histogram, boxplot) to avoid client-side plotting dependencies. Templates are intentionally simple to remain implementable by one developer within the project timeframe. AI assistance: GitHub Copilot suggested template layouts, utilities for embedding matplotlib images in HTML, and small styling snippets to improve readability.

### Frontend (Minimal)

Purpose: Provide a single-page upload form and a lightweight results viewer that fetches the HTML or JSON outputs; emphasis is on local usability rather than a polished UX. The frontend uses static HTML/CSS with minimal JavaScript to keep scope realistic for an individual student. AI assistance: GitHub Copilot produced concise fetch patterns and form-handling snippets that served as a clear starting point.

### Testing and Documentation

Purpose: Include a small unit-test suite for core validators, a README with setup and usage instructions, and example datasets to demonstrate reproducibility. Tests target deterministic behaviors and run quickly on a developer machine. AI assistance: GitHub Copilot generated initial test cases, README sections, and example commands that were refined to match the constrained scope of the assignment.
