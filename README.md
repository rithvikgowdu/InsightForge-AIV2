# InsightForge AI

> **Turning Real User Problems into Product Opportunities.**

InsightForge AI discovers real user problems from public GitHub discussions, extracts recurring friction points using semantic embeddings and clustering, and synthesizes structured SaaS product opportunities with actionable MVP requirements, traceable evidence, and transparent confidence indicators.

---

## 1. System Architecture & Features

- **Semantic Intelligence Pipeline:**
  - Ingests public GitHub issues with pagination, rate-limit resilience, and PR exclusion.
  - Cleans boilerplate, markdown templates, and bot comments, deduplicating issues by text hash.
  - Computes dense embeddings with Sentence-Transformers (`all-MiniLM-L6-v2`) and deterministic TF-IDF fallback.
  - Clusters semantically related complaints via DBSCAN & Agglomerative clustering.
  - Synthesizes actionable product opportunities (problem statement, business value, proposed solution, target persona, suggested MVP features).
  - Clearly identifies whether opportunities were generated via configured LLM (Ollama / hosted) or deterministic heuristic fallback.
- **Enterprise Security & Authentication:**
  - Bcrypt salted password hashing.
  - Cryptographically signed JWT tokens (24-hour default expiration).
  - Strict user data isolation: users cannot access or view another user's analysis history.
- **Modern Responsive SaaS Interface:**
  - Next.js (App Router), TypeScript strict mode, and Tailwind CSS.
  - Real-time progress polling with step-by-step pipeline status.
  - Searchable source evidence modal with direct links and verbatim quotes.

---

## 2. Prerequisites

- **Python:** 3.10 to 3.14
- **Node.js:** v18.x to v26.x (npm included)
- **Database:** PostgreSQL 15+ (recommended for production/Docker) or SQLite (used automatically for local dev/testing if no Postgres specified)
- **Docker & Docker Compose** (optional for containerized setup)

---

## 3. Quick Start (Local Development)

### 3.1 Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
cp ../.env.example .env

# 5. Run database migrations to head
alembic upgrade head

# 6. Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The FastAPI interactive documentation will be available at [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs).

---

### 3.2 Frontend Setup

```bash
# 1. Navigate to frontend directory in another terminal
cd frontend

# 2. Install dependencies
npm install

# 3. Start Next.js development server
npm run dev
```

The application will be live at [http://localhost:3000](http://localhost:3000).

---

## 4. Running with Docker Compose

To start the entire stack (PostgreSQL with pgvector, FastAPI backend, and Next.js frontend):

```bash
docker-compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **PostgreSQL:** Port `5432`

---

## 5. Environment Variables Configuration

Copy `.env.example` to `.env`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./insightforge.db` or `postgresql://...` |
| `SECRET_KEY` | Secret key for signing JWT tokens | Generate random 32+ char string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` (24 hours) |
| `GITHUB_TOKEN` | Optional GitHub Personal Access Token (PAT) for 5,000 req/hr rate limits | Optional |
| `LLM_PROVIDER` | `deterministic_fallback`, `ollama`, or `hosted` | `deterministic_fallback` |
| `LLM_MODEL` | Target model name | `llama3.2` |
| `LLM_API_KEY` | Hosted LLM API key | Optional |
| `LLM_API_BASE_URL` | LLM OpenAI-compatible endpoint | `http://localhost:11434/v1` |
| `NEXT_PUBLIC_API_URL` | Frontend API client target | `http://localhost:8000/api/v1` |

---

## 6. Running Automated Tests

### Backend Test Suite (Pytest)

```bash
cd backend
source .venv/bin/activate
pytest -v
```

This verifies:
- User registration, duplicate constraint enforcement, and password verification.
- JWT token generation, expiration, and invalidation.
- Protected route authentication and data isolation between users.
- Mocked GitHub connector behavior (rate limit handling, 404s, pull request filtering).
- Text preprocessing, markdown stripping, and deduplication.
- Semantic clustering edge cases and TF-IDF embedding normalization.
- Deterministic opportunity synthesis and confidence score calculation.
- End-to-end background pipeline execution and database persistence.
- Health (`/api/v1/health`) and readiness (`/api/v1/health/ready`) probes.

### Frontend Linting & Build

```bash
cd frontend
npm run lint
npm run build
```

---

## 7. Cloud Deployment (Vercel & Render)

InsightForge AI is pre-configured for cloud deployment:
- **Backend on Render:** Auto-provisions PostgreSQL and FastAPI using [`render.yaml`](./render.yaml).
- **Frontend on Vercel:** Next.js App Router deployed from the `frontend/` directory with [`frontend/vercel.json`](./frontend/vercel.json).

For full step-by-step instructions, see the **[Production Deployment Guide](./docs/DEPLOYMENT.md)**.

---

## 8. Troubleshooting

- **GitHub API Rate Limits:** Without a `GITHUB_TOKEN`, GitHub limits unauthenticated requests to 60/hour per IP. Add a personal access token to your `.env` file as `GITHUB_TOKEN=ghp_...` to unlock 5,000 requests/hour.
- **LLM Unavailable:** If Ollama or hosted providers are unreachable, InsightForge AI automatically activates its deterministic heuristic pipeline. The output is clearly labeled with an amber badge and explains the confidence scoring rationale without hallucinating data.
- **Database Reset:** To wipe and re-run migrations in local SQLite development:
  ```bash
  rm -f backend/insightforge.db
  cd backend && alembic upgrade head
  ```

