# InsightForge AI — System Architecture & Technical Specifications

**Tagline:** Turning Real User Problems into Product Opportunities.

---

## 1. Architectural Overview

InsightForge AI is an integrated, full-stack intelligence platform that discovers unmet user demand from public developer discussions (GitHub issues, bug reports, and feature requests) and synthesizes them into actionable, high-confidence SaaS product opportunities.

```mermaid
flowchart TD
    User([User / Browser]) <--> NextApp[Next.js App Router Frontend]
    NextApp <--> FastApiApp[FastAPI Backend /api/v1]
    
    subgraph Backend_Services[FastAPI Backend Engine]
        FastApiApp --> AuthSecurity[Auth & JWT Security Service]
        FastApiApp --> AnalysisRouter[Analysis Orchestrator]
        
        AnalysisRouter --> GhConnector[GitHub REST API Connector]
        AnalysisRouter --> Preprocessor[NLP Text Preprocessor]
        AnalysisRouter --> Embeddings[Sentence-Transformers Embeddings]
        AnalysisRouter --> Clustering[Density & Agglomerative Clustering]
        AnalysisRouter --> LLMOrchestrator[LLM / Deterministic Fallback Engine]
        AnalysisRouter --> BgWorker[Persistent Background Worker]
    end

    subgraph Storage[Data Persistence]
        FastApiApp <--> DB[(PostgreSQL / SQLite via SQLAlchemy 2.x)]
        DB --- Migrations[Alembic Migrations]
    end
```

---

## 2. Core Modules & Responsibilities

### Frontend (`frontend/`)
- **Framework:** Next.js 16 (App Router) with React 19 and TypeScript.
- **Styling & UI:** Tailwind CSS, Lucide React, accessible contrast, responsive breakpoints (mobile, tablet, desktop).
- **Client Layer:** Centralized typed API client (`src/lib/api.ts`), persistent session context (`src/lib/auth-context.tsx`), and error boundary handling.
- **Key Views:**
  - `/`: Public landing page with live sample opportunity report and architecture explanation.
  - `/login` & `/register`: Secure authentication forms with real-time feedback.
  - `/dashboard`: High-level SaaS metrics and recent analysis run list.
  - `/dashboard/new`: Repository analysis submission form with preset exploration chips.
  - `/dashboard/analysis/[id]`: Real-time polling progress bar, problem clusters, and structured opportunity cards with traceable evidence modals.
  - `/dashboard/history`: Persisted search and filterable table of past analyses with delete actions.
  - `/dashboard/account`: Profile, session details, and security controls.

### Backend (`backend/app/`)
- **Framework:** FastAPI with Python 3.14 / 3.12 compatibility.
- **Validation:** Pydantic v2 schemas (`app/schemas/`).
- **ORM:** SQLAlchemy 2.0 with strict foreign key constraints, cascade deletes, and timezone-aware timestamps.
- **Database Migrations:** Alembic (`alembic/`) with versioned revision history.
- **Security:** Bcrypt salted password hashing and cryptographically signed JWT access tokens.
- **User Data Isolation:** Enforced at the repository level; users cannot view, poll, or modify analyses belonging to another user.

---

## 3. The AI & NLP Analysis Pipeline

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI API
    participant Worker as Background Worker
    participant GH as GitHub API
    participant NLP as Preprocessor & Embeddings
    participant Cluster as Clustering Engine
    participant LLM as LLM / Fallback Engine
    participant DB as Database

    User->>API: POST /api/v1/analysis (repo_url)
    API->>DB: Create AnalysisRun (QUEUED)
    API->>Worker: Dispatch task asynchronously
    API-->>User: 202 Accepted (AnalysisRun metadata)
    
    Worker->>DB: Update status to RUNNING (15%)
    Worker->>GH: Validate repo and fetch public issues
    GH-->>Worker: Return raw issues (excluding PRs)
    
    Worker->>DB: Update status to RUNNING (50%)
    Worker->>NLP: Clean markdown, strip bot boilerplate, deduplicate
    NLP-->>Worker: Clean document texts
    
    Worker->>DB: Update status to RUNNING (65%)
    Worker->>NLP: Generate normalized dense embeddings (all-MiniLM-L6-v2)
    NLP-->>Worker: Embedding matrix (N x D)
    
    Worker->>DB: Update status to RUNNING (78%)
    Worker->>Cluster: Run DBSCAN / Agglomerative clustering
    Cluster-->>Worker: Identified semantic clusters & outliers
    
    Worker->>DB: Update status to RUNNING (90%)
    Worker->>LLM: Synthesize problem statements, solutions, & MVP features
    LLM-->>Worker: Structured opportunities & calculated confidence
    
    Worker->>DB: Bulk insert Issues, Clusters, & Opportunities (100%)
    Worker->>DB: Update status to COMPLETED
    User->>API: GET /api/v1/analysis/{id}
    API-->>User: Full Analysis Detail & Structured Opportunities
```

### Deterministic Heuristic Fallback
When third-party LLMs (Ollama or hosted APIs) are offline or unconfigured:
1. The engine deterministically analyzes problem indicators (`fail`, `crash`, `broken`, `timeout`, `leak`, `missing`, `slow`).
2. Synthesizes pain statements, target customer segments, and 4 specific MVP requirements.
3. Calculates confidence score transparently:
   $$\text{Score} = 0.65 + \min(0.15, N \times 0.02) + \min(0.10, \text{Comments} \times 0.005) + 0.05$$
4. Clearly flags output as `is_fallback = true` with full explanation.

---

## 4. Database Schema

- `users`: ID, unique username, unique email, bcrypt hashed password, active flag, timestamps.
- `analysis_runs`: UUID primary key, `user_id` foreign key, repository metadata, status enum (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`), progress percentage, current step, counts, `is_fallback` flag, error message.
- `collected_issues`: Issue number, title, body, cleaned text, GitHub URL, author, labels JSON, comment count, cluster reference.
- `analysis_clusters`: Cluster label, title, summary, size, recurring themes JSON, sample issue numbers.
- `product_opportunities`: Title, problem statement, business opportunity, proposed solution, customer segment, MVP features list JSON, market potential, confidence score, confidence explanation, supporting evidence quotes JSON, fallback flag.

