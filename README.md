# RupeeRadar

AI-powered personal finance assistant that analyzes bank statement data and turns messy transactions into categorized spending insights.

---

## What is this project?

RupeeRadar is an end-to-end web application that processes raw, messy financial statements (starting with CSV bank exports) and converts them into structured financial insights. It consists of a FastAPI Python backend pipeline and a React/TypeScript frontend dashboard.

The core workflow parses raw text, cleans UPI/bank boilerplate strings, runs a hybrid rule-based and LLM-assisted categorizer, detects recurring transactions (subscriptions, rent, EMIs, SIPs), calculates personal finance metrics, and dynamically generates actionable insights for the user.

### Key Capabilities
- **Statement Ingestion**: Automatically detects headers and formats (CSV, with PDF and Excel support coming in later phases).
- **Transaction Cleaning**: Normalizes noisy merchant strings (e.g., stripping UPI/IMPS reference hashes).
- **Hybrid Categorization**: Automatically places expenses into 10 target categories like Food, Travel, Shopping, Salary, Rent, and Investments.
- **Recurrence Tracking**: Flags repeat payments and estimates monthly commitments.
- **Interactive Dashboard**: Visualizes income, spending, savings rate, and category splits.
- **Narrative Insights**: Generates personalized spending observations.
- **Shareable Reports**: Supports PDF/HTML reports exporting summarized statements.
- **Privacy First**: Processes statements ephemerally with automatic 1-hour session expiration (TTL) and zero persistent storage of raw statement files.

### Project Structure
- [backend/](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend) - FastAPI pipeline, rules, and LLM integrations.
- [frontend/](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/frontend) - React/Vite/TypeScript interface.
- [sample_data/](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/sample_data) - Realistic test statements for ingestion verification.
- [Docs/](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/Docs) - System architecture, implementation plans, and analysis logs.

---

## Why should I care?

Managing personal finances using bank statement exports is incredibly frustrating:
1. **Messy Data**: Real-world statements contain inconsistent descriptions with cryptic UPI handles (e.g., `UPI/1234567890/Swiggy/Paytm@okaxis`), IMPS numbers, or merchant codes instead of clean business names.
2. **Tedious Manual Work**: Standard tools require you to manually tag hundreds of transactions or write complex spreadsheet formulas to categorize transactions.
3. **Hidden Subscriptions**: Small recurring charges (like SaaS, streaming, or SIPs) accumulate quietly, making it hard to see your total fixed monthly commitments.
4. **Privacy Concerns**: Many commercial finance apps scrape your messages or store your complete bank history on their servers indefinitely, creating significant security risks.

**RupeeRadar solves all of these problems**:
- **Automated Cleaning & Mapping**: It instantly parses and simplifies messy UPI narratives.
- **Hybrid Intelligence**: Combining instant, deterministic keyword rules with optional Groq LLM fallback ensures high-accuracy categorization without manual tagging.
- **Auto-Recurring Detection**: It identifies subscriptions, EMIs, rent, and investments by analyzing amount consistency and monthly interval patterns.
- **Absolute Privacy**: It runs locally or ephemerally; you can purge your session data with a single click (or let the session TTL expire), ensuring your sensitive financial information is never retained.

---

## How do I run it?

### Quick Start (Docker Compose)
The easiest way to run the entire project is using Docker Compose, which boots up both the frontend and backend containers:

```bash
docker compose up --build
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Manual Local Run

#### Prerequisites
- **Python**: Version 3.12+
- **Node.js**: Version 20+
- **Groq API Key** (optional): Needed if running LLM enrichment (Phase 5+) — [console.groq.com](https://console.groq.com/)

#### 1. Environment Setup
Copy the template environment file to create your local configurations:
```bash
cp .env.example .env
```
> [!NOTE]
> Update the `.env` file to set `GROQ_API_KEY` and toggle `ENABLE_LLM=true` if you wish to run the LLM-powered categorization and insights.

#### 2. Run the Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- **Backend Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 3. Run the Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
- **App URL**: [http://localhost:5173](http://localhost:5173)

#### 4. Run Backend Tests
To execute the unit and integration tests:
```bash
cd backend
pytest
```

#### 5. Manual Testing with Sample Data
Use the realistic sample statement [sample_data/sample_statement.csv](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/sample_data/sample_statement.csv) (72 mock Indian bank transactions) to upload in the UI and test the parser pipeline.

---

## How is it built?

RupeeRadar uses a modular, layered pipeline architecture split into a React client and a FastAPI server.

```
Upload Statement → Ingestion Parser → Transaction Cleaner → Hybrid Categorizer → Recurrence Detector → Analytics Engine → Insight Generator → UI / PDF Report
```

### Technology Stack
- **Frontend**:
  - **React 19** & **TypeScript** for structured, responsive layouts.
  - **Vite** for optimized assets and quick development feedback.
  - **Tailwind CSS (v4)** for modern visual styling.
  - **Recharts** for interactive finance charts.
  - **Lucide React** for modern UI icons.
  - Dependencies configured in [frontend/package.json](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/frontend/package.json).
- **Backend**:
  - **FastAPI** (Python 3.12) serving REST endpoints.
  - **Pandas** for ingestion, statement formatting, and analytics aggregation.
  - **Pydantic & Pydantic-Settings** for strict request/response schemas and settings validation.
  - **Groq SDK** for LLM categorization fallback and insight enrichment.
  - **Pytest** for testing.
  - Dependencies configured in [backend/requirements.txt](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/requirements.txt).

### API Endpoints
The backend [backend/app/main.py](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/main.py) exposes the following API routes:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Service status, database check, and Groq connection verification. |
| POST | `/api/v1/analyze` | Accepts multipart CSV statement files, triggers the pipeline, and returns the analysis. |
| GET | `/api/v1/analyze/{job_id}` | Retrieves a previously stored analysis by job ID. |
| GET | `/api/v1/analyze/{job_id}/transactions` | Returns paginated transactions, filterable by category and recurrence. |
| DELETE | `/api/v1/analyze/{job_id}` | Immediately purges all ephemeral job data from memory/temp storage. |

### Environment Config
Variables configured in [backend/app/settings.py](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/settings.py) and mapped from [.env.example](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/.env.example):
- `GROQ_API_KEY`: API key for Groq LLM integration.
- `GROQ_MODEL`: Model used (defaults to `llama-3.3-70b-versatile`).
- `ENABLE_LLM`: Feature flag to enable or disable Groq LLM integration.
- `SESSION_TTL_MINUTES`: Expiration time for ephemeral data storage (defaults to `60`).

### Pipeline Logic & Code Symbols
- Ingestion occurs via [parse_csv](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/ingestion/csv_parser.py) using a flexible column detection mechanism.
- The pipeline execution orchestrator [run_analysis](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/orchestrator.py#L27-L136) runs these stages sequentially:
  1. [clean](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/cleaner.py): Cleans strings and models raw data as [RawTransaction](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/transaction.py#L22-L29) items before transforming them to [Transaction](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/transaction.py#L32-L45) objects.
  2. [categorize](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/categorizer/rules.py): Tags transactions with custom [Category](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/transaction.py#L8-L19) values using keyword rules, with fallback to an LLM classifier.
  3. [detect_recurring](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/recurrence.py): Group repetitive transactions into a [RecurringGroup](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/transaction.py#L64-L74).
  4. [compute_metrics](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/analytics.py): Calculates aggregated [FinancialMetrics](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/analysis.py#L30-L43).
  5. [generate_insights](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/pipeline/insights.py): Creates deterministic template-based and LLM-enriched [Insight](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/analysis.py#L52-L59) models.
  6. Returns a full [AnalysisResult](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/backend/app/models/analysis.py#L77-L89) package containing transactions, recurring items, metrics, and insights.

---

### Detailed Design & Project Roadmap
For deeper details on development plans and architecture, explore the documentation:
- **System Architecture**: [Docs/architecture.md](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/Docs/architecture.md)
- **Project Scope & Context**: [Docs/context.md](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/Docs/context.md)
- **Phase-Wise Roadmap**: [Docs/implementation-plan.md](file:///c:/Users/loq/OneDrive/Desktop/RupeeRadar/Docs/implementation-plan.md)
