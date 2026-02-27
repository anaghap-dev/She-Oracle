# SHE-ORACLE — Autonomous Opportunity & Protection AI for Women

Multi-agent autonomous AI system for women empowerment. Powered by **Google Gemini**, **ChromaDB RAG**, and a **ReAct planning loop**.

## Stack
| Layer | Tech |
|---|---|
| Frontend | React + Vite + TailwindCSS |
| Backend | Node.js + Express (API Gateway) |
| Orchestrator | Python + FastAPI |
| LLM | Google Gemini 2.0 Flash |
| Vector DB | ChromaDB (local) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |

## Setup

### 1. Add your Gemini API key
```bash
# Edit orchestrator/.env
GEMINI_API_KEY=your_actual_key_here
```

### 2. Python Orchestrator
```bash
cd orchestrator
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

# Seed the knowledge base (ONE TIME ONLY)
python rag/seed_knowledge.py

# Start the orchestrator
uvicorn main:app --reload --port 8000
```

### 3. Node.js Backend
```bash
cd backend
npm install
npm start
```

### 4. React Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## Architecture
```
React UI (5173)
  → Node.js Backend (3001)    [API Gateway + SSE Proxy]
    → Python FastAPI (8000)   [Agent Orchestrator]
      → Gemini API            [LLM Reasoning]
      → ChromaDB              [RAG Knowledge Base]
        ← Indian Labor Laws
        ← Government Schemes
        ← Scholarships
        ← Grants Programs
```

## Agent Flow (ReAct Loop)
1. **Planner** decomposes goal into subgoals
2. **Retriever** fetches relevant knowledge from ChromaDB
3. **Tools** (`grant_finder`, `legal_rights_checker`, `resume_analyzer`, `income_projection`, `risk_assessment`) execute
4. **Planner** synthesizes all intelligence into structured plan
5. **Critic** evaluates feasibility/risk/timeline (replans if score < 6/10)
6. **Memory** persists context across sessions

## Domains
- **Career** — Resume analysis, skill gaps, upskilling roadmaps
- **Legal** — POSH Act, Maternity Benefit, Equal Remuneration, escalation strategies
- **Financial** — Income projections, multiple income streams, FI roadmaps
- **Education** — Scholarships, fellowships, free skill programs
- **Grants** — Government schemes, startup funding, incubators
