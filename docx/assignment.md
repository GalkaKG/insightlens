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


## Development Process per Module

### 1. API Layer

- **Approach & reasoning:** Use a minimal, well-typed FastAPI surface to expose upload, analysis, and report retrieval as reproducible programmatic operations. Prioritise clear Pydantic models and small, testable route handlers so the API is maintainable by an individual developer.
- **Step-by-step workflow:** Scaffold a FastAPI app and router; ask Copilot to generate Pydantic models for file metadata and validation configuration; generate route handlers (`/upload`, `/analyze`, `/report/{id}`) that delegate to helper functions; add utilities for temporary file handling and response formatting; iterate with Copilot to refine type hints and error handling.
- **Testing strategy:** Use FastAPI TestClient for unit tests that validate status codes, schema conformance, and error paths (bad file, oversized upload). Add integration tests that mock downstream modules to verify routing and error propagation.
- **AI tool choice:** GitHub Copilot — chosen for editor-integrated, idiomatic FastAPI suggestions and rapid scaffolding.
- **Key prompts or interactions:**
  - "Generate a FastAPI POST `/upload` endpoint that accepts a file and returns a JSON id using Pydantic."
  - "Create a Pydantic model for validation configuration with optional thresholds and regex fields."
  - "Show an example FastAPI TestClient test for `/analyze` returning HTML."

### 2. Data Ingestion and Parsing

- **Approach & reasoning:** Implement deterministic helpers that canonicalize inputs into pandas DataFrames and surface parsing errors clearly; favour explicit behavior to ensure reproducibility for coursework.
- **Step-by-step workflow:** Implement `read_table` to select CSV vs single-sheet Excel with safe pandas defaults; add normalization helpers (`normalize_column_names`, `trim_strings`, `standardize_missing_values`); use Copilot to scaffold try/except wrappers mapping parser exceptions to user-facing errors; include a size-check helper enforcing the target dataset limit.
- **Testing strategy:** Unit tests using representative files (clean CSV, malformed CSV, Excel with NA markers) and tests for normalization functions; assert deterministic dtypes under fixed configuration.
- **AI tool choice:** GitHub Copilot — used for pandas idioms and exception-handling scaffolds.
- **Key prompts or interactions:**
  - "Generate a `read_table(path, max_rows=100000)` helper that selects CSV or Excel and returns a DataFrame or raises a descriptive exception."
  - "Create a small function to normalize column names to snake_case and trim whitespace."
  - "Show a pytest case for reading a CSV with inconsistent NA markers."

### 3. Validation Engine

- **Approach & reasoning:** Build compact, rule-based validators with clear inputs/outputs so each rule is composable and simple to unit-test; prioritise deterministic JSON-serializable results.
- **Step-by-step workflow:** Define a `Validator` function signature and dispatcher; implement `missingness_validator`, `type_consistency_validator`, `duplicate_detector`, and `iqr_outlier_detector`; use Copilot to scaffold serialization helpers that produce a unified JSON schema and human-readable summaries; add a small config loader for thresholds.
- **Testing strategy:** Unit tests for each validator using synthetic DataFrames that exercise edge cases (all-NA, mixed types, identical rows, numeric outliers); assert stable JSON output ordering for reliable assertions.
- **AI tool choice:** GitHub Copilot — used to propose concise validator implementations and test skeletons.
- **Key prompts or interactions:**
  - "Implement a `missingness_validator(df, threshold)` returning columns exceeding the threshold with counts and percentages."
  - "Create `iqr_outlier_detector(column)` that returns lower/upper fence outliers and an example unit test."
  - "Serialize validator results into a compact JSON schema with keys: `rule`, `severity`, `details`."

### 4. Reporting Layer

- **Approach & reasoning:** Produce reproducible, self-contained artifacts (static HTML via Jinja2 and compact JSON) with embedded images to avoid client-side plotting dependencies; focus on clarity for coursework submission.
- **Step-by-step workflow:** Create a Jinja2 template for a single-page HTML report; implement matplotlib helpers that return PNG bytes and a utility to embed images as base64; ask Copilot to scaffold the template and embedding utilities and refine layout and headings; implement a JSON exporter mirroring the HTML content.
- **Testing strategy:** Render reports for example datasets and assert expected sections and JSON fields; include base64 round-trip tests and manual visual sanity checks.
- **AI tool choice:** GitHub Copilot — used to draft templates and utilities for embedding matplotlib figures.
- **Key prompts or interactions:**
  - "Generate a simple Jinja2 HTML template for a report with placeholders for a summary table and images."
  - "Provide a helper `plot_histogram(series)` that returns PNG bytes suitable for embedding."
  - "Create a function to convert matplotlib PNG bytes to a base64 data URL for inclusion in HTML."

### 5. Frontend (Minimal)

- **Approach & reasoning:** Implement a single static page with an upload form and lightweight fetch logic to exercise the API; prioritise clarity and minimal dependencies to keep scope achievable for one developer.
- **Step-by-step workflow:** Create `index.html` with an upload form and results container; generate `main.js` with `fetch` POST logic to submit files and retrieve reports; use Copilot for concise fetch examples and error handling; keep CSS minimal and inline to avoid build steps.
- **Testing strategy:** Manual end-to-end checks in the development environment (upload sample files and inspect results); optional headless-browser smoke tests for basic flows.
- **AI tool choice:** GitHub Copilot — used for fetch patterns and form handling scaffolds.
- **Key prompts or interactions:**
  - "Create an `index.html` upload form and JavaScript that posts a file to `/upload` and renders returned HTML into a container."
  - "Provide a `fetch` example with progress/error handling and JSON parse fallback."

### 6. Testing and Documentation

- **Approach & reasoning:** Provide a compact pytest suite and clear README to ensure reproducibility and assessability; tests emphasise deterministic units and rapid execution.
- **Step-by-step workflow:** Create a `tests/` folder with unit tests for ingestion helpers, validators, and report serialization; use Copilot to scaffold fixtures and example test-data helpers; draft `README.md` containing setup, run, and test commands and explicit scope/out-of-scope notes.
- **Testing strategy:** Run the test suite locally during development; include example datasets under `examples/` and use `pytest -q` for CI-friendly execution; prefer small, deterministic tests for grading ease.
- **AI tool choice:** GitHub Copilot — used for initial test scaffolding and README templates which were curated for reproducibility.
- **Key prompts or interactions:**
  - "Create pytest fixtures for sample DataFrames and an example test for the missingness validator."
  - "Generate a README section with virtualenv setup, install, and run instructions for the FastAPI app and tests."
  - "Show a pytest invocation and expected output snippet for a passing test suite."


## Challenges & Tool Comparison

### Technical challenges

- Pandas edge cases: mixed-type columns, silent dtype coercion, and inconsistent NA markers complicated reliable summaries; date parsing and Excel cell formats required explicit dtype handling to avoid downstream errors. Large-ish tables exposed memory pressure on a developer laptop, motivating conservative defaults (e.g., max row limits) and explicit dtype inference.
- FastAPI file handling: managing multipart uploads, enforcing size limits, and converting uploaded streams into deterministic temporary files required careful error handling; synchronous pandas reads in request handlers needed isolation to avoid blocking during local development.
- Template embedding: producing self-contained HTML reports with embedded images required converting matplotlib outputs to base64 and ensuring templates remained readable; embedding large images increased memory use and report size.
- Deterministic testing: ensuring reproducible tests demanded fixed random seeds for plots, stable ordering in serialized results, and fixtures for representative input files; filesystem timestamps and floating-point tolerances had to be normalized in assertions.

### AI tool comparison

- GitHub Copilot: most useful for rapid scaffolding—route handlers, Pydantic schemas, pandas read idioms, Jinja2 snippets, and basic unit-test skeletons. It accelerated mechanical implementation while leaving design choices to the developer.
- Claude Code / reasoning assistants: valuable for higher-level design discussions and clarifying trade-offs (e.g., synchronous vs async processing) and suggesting test-case ideas; useful when mapping architectural alternatives rather than line-by-line code.
- Specialized coding assistants (Augment, Cursor): helpful for repository-wide refactors or multi-file generation when scaling beyond a single-developer prototype; for this student project they were optional.

### Suggestions for continued development

- Performance: add chunked or incremental reading, allow user-supplied dtype hints, or adopt Dask/Modin for larger datasets; move long-running analyses to background tasks (Celery/RQ) to keep request handlers responsive.
- Richer visualizations: introduce interactive plots (Plotly or Vega) behind optional toggles and provide lazy-loading of heavy visuals to limit initial report size.
- Extended validation: add schema-based checks (e.g., pandera), semantic validators (cross-field rules), and configurable severity levels for automated gating.
- API & deployment: add background processing and simple authentication for multi-user demos, and containerize the application for reproducible deployment while keeping these optional to preserve the project’s single-developer scope.
- Testing & reproducibility: expand deterministic fixtures, include data versioning for example datasets, and add lightweight CI to run the pytest suite on push.
