# RupeeRadar

AI-powered personal finance assistant that analyzes bank statement data and turns messy transactions into categorized spending insights.

## Features (planned)

- CSV bank statement upload (Excel & PDF in later phases)
- Transaction cleaning and categorization
- Recurring payment detection (subscriptions, EMIs, rent, SIPs)
- Spend summary dashboard with insights
- Shareable report export
- **LLM:** [Groq](https://groq.com/) for categorization fallback and insight enrichment (Phase 5)

## Project structure

```
RupeeRadar/
├── backend/          # FastAPI pipeline + Groq integration
├── frontend/         # React + Vite + Tailwind + Recharts
├── sample_data/      # Test bank statements
└── Docs/             # Context, architecture, implementation plan
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Groq API key (optional until Phase 5) — [console.groq.com](https://console.groq.com/)

## Quick start (local)

### 1. Environment

```bash
cp .env.example .env
# Optional for Phase 5+: set GROQ_API_KEY and ENABLE_LLM=true
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

### 4. Docker Compose

```bash
docker compose up --build
```

## Sample data

Use `sample_data/sample_statement.csv` (72 realistic Indian bank transactions) for manual testing once the analysis pipeline is implemented in Phase 1–2.

Golden test files planned for later phases:

- `upi_food.csv`
- `mixed_spend.csv`
- `recurring_heavy.csv`

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Service health + Groq LLM status |
| POST | `/api/v1/analyze` | Upload CSV statement; returns full analysis |
| GET | `/api/v1/analyze/{job_id}` | Retrieve stored analysis result |
| GET | `/api/v1/analyze/{job_id}/transactions` | Paginated transactions (`page`, `size`, `category`, `recurring`) |
| DELETE | `/api/v1/analyze/{job_id}` | Purge session data |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Example analysis output: `sample_data/sample_analysis_output.json`

## Groq configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model for categorization & insights |
| `ENABLE_LLM` | `false` | Enable Groq in pipeline (Phase 5) |

## Development phases

See [Docs/implementation-plan.md](./Docs/implementation-plan.md). **Phase 2** completes the backend API pipeline; frontend integration is Phase 3.

## Tests

```bash
cd backend
pytest
```

## License

MIT (adjust as needed for your submission)
