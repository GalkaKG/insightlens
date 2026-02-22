# InsightLens

InsightLens is a modular FastAPI web application designed to perform automated data quality validation and exploratory data analysis (EDA) on CSV and Excel datasets using pandas.

The project demonstrates clean backend architecture, separation of concerns, and AI-assisted software development practices using GitHub Copilot.

---

---

## Development

Create and activate a Python virtual environment, install dependencies, run the app and tests.

Windows (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the app locally with Uvicorn:

```powershell
.\\.venv\\Scripts\\python -m uvicorn app:app --reload --port 8000
```

Run the unit tests:

```powershell
.\\.venv\\Scripts\\python -m pytest -q
```

## 🚀 Overview

Before datasets are used in machine learning models, analytics pipelines, or production systems, they must be validated for structural integrity and quality issues. InsightLens provides a lightweight web interface and API endpoints that automatically analyze uploaded datasets and return structured validation reports.

The system focuses on backend engineering principles rather than AI integration, showcasing how modern AI coding assistants can accelerate development while maintaining architectural control and code quality.

---

## ✨ Core Features

- 📂 CSV and Excel file upload
- 📊 Dataset shape and structure summary
- ❗ Missing value detection (count & percentage)
- 🔁 Duplicate row detection
- ➖ Negative numeric value validation
- 📈 IQR-based outlier detection
- 📄 Structured JSON response
- 🧪 Unit testing with pytest
- 📚 Automatic Swagger API documentation

---

## 🏗 Architecture

The application follows a modular architecture:

- **API Layer** – FastAPI routes and request handling
- **Services Layer** – Data loading and validation logic
- **Validation Engine** – Reusable rule-based data checks
- **Reporting Layer** – Structured output for API/UI consumption
- **Testing Layer** – Unit tests ensuring correctness

This separation ensures maintainability, scalability, and clean integration between components.

---

## 🛠 Tech Stack

- Python 3.11+
- FastAPI
- pandas
- NumPy
- Jinja2
- pytest
- Uvicorn

---

## 🤖 AI-Assisted Development

This project was developed using GitHub Copilot as an AI coding assistant. The development process involved iterative prompting, refinement, architectural restructuring, and manual correction to ensure production-ready quality.

The goal was not to integrate AI into the system, but to demonstrate how AI can assist software engineers during:

- Architecture planning
- Code generation
- Refactoring
- Test generation
- Debugging

---
