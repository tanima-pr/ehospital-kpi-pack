# eHospital — Governed AI Query Layer

An AI layer that sits on top of the [eHospital KPI Pack](../README.md) and lets a
non-technical user ask questions in plain English — *"weekly cancellation rate",
"billing split by insurance type", "top doctors by completed appointments"* — and get
back a **governed, guardrail-checked SQL answer**.

The AI never sees raw patient data. It only sees the schema and the **KPI definitions
taken straight from the KPI pack**, so it answers with *your* metric logic instead of
guessing. Every generated query is validated before it runs, executed read-only, and
written to an audit log.

> **Privacy:** this demo runs on **synthetic data** generated locally by `setup_db.py`.
> No real patient information (PHI) is ever stored or committed. The same engine points
> at the real `EHOSPITAL_DW` warehouse by swapping the connection.

## Architecture

```
Question ─▶ RAG retrieval ─▶ LLM generates SQL ─▶ Guardrails ─▶ Read-only run ─▶ Answer
           (KPI definitions)   (grounded, temp=0)   (validate)     (+ audit log)
```

| Stage | File | What it does |
|------|------|--------------|
| Knowledge | `knowledge_base.py` | Schema + KPI definitions + example Q→SQL pairs (the governed source of truth) |
| Retrieval | `rag.py` | Embeds the question, pulls the most relevant KPI definitions |
| Generation | `llm.py` | Sends definitions + question to the model, gets SQL back (temperature 0) |
| Safety | `guardrails.py` | Blocks non-SELECT / injection / non-approved tables; runs read-only; logs every attempt |
| UI | `app.py` | Streamlit app showing retrieval, SQL, guardrail verdict, and result |
| CLI | `ask_cli.py` | Same loop in the terminal |
| Data | `setup_db.py` | Builds the synthetic `ehospital_dw.db` (mirrors the real star schema) |

Approved tables: `dim_patient`, `fact_appointments`, `fact_billing`, `fact_bloodtests`.

## Run it

```bash
cd ai_assistant
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then paste your FREE Gemini key (starts with AIza)
python setup_db.py            # builds synthetic ehospital_dw.db

streamlit run app.py          # clickable demo
# or:  python ask_cli.py      # terminal demo
```

Ask *weekly cancellation rate* and watch it work. Then ask *delete all appointments*
and watch the guardrails refuse it on screen.

## Why this matters (the governance story)

Healthcare analytics can't just "run whatever the AI wrote." This layer enforces:

- **Grounded metrics** — cancellation rate, revenue, OHIP-vs-private billing are defined
  once, in `knowledge_base.py`, and reused on every answer (no hallucinated definitions).
- **SQL validation** — `sqlglot` parsing blocks anything that isn't a single SELECT on an
  approved table, and blocks stacked-statement injection.
- **Read-only execution** — the database is opened `mode=ro`; writes are physically impossible.
- **Audit trail** — every question, the SQL, and the verdict are appended to `queries.log`.

## Tech

Python · SQLite (synthetic mirror of MySQL `EHOSPITAL_DW`) · Google Gemini (free tier)
via OpenAI-compatible API · RAG with embeddings + cosine similarity · sqlglot · Streamlit.
