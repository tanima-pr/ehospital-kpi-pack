"""
app.py — the clickable eHospital AI query layer.
Run it with:   streamlit run app.py

Plain-English question -> retrieve governed KPI definitions (RAG) -> generate SQL
-> guardrail check -> read-only run -> answer, with a full audit trail.
The AI only ever sees the schema + metric definitions, never raw patient data.
"""
import os
import streamlit as st

# --- Cloud deploy support ---------------------------------------------------
# On Streamlit Community Cloud there is no .env file. Secrets are pasted into the
# app dashboard and exposed via st.secrets. Copy them into os.environ BEFORE the
# engine imports below, since rag.py contacts the embedding API as it loads.
# Locally there is no secrets file, so this is skipped and .env is used instead.
try:
    for _k in ("GEMINI_API_KEY", "PROVIDER"):
        if _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

from llm import ask
from rag import retrieve
from guardrails import validate_sql, run_readonly, audit_log
import setup_db

DB = os.path.join(os.path.dirname(__file__), "ehospital_dw.db")
APPROVED_TABLES = ["dim_patient", "fact_appointments", "fact_billing", "fact_bloodtests"]

# On a fresh cloud container the synthetic DB won't exist yet — build it once.
if not os.path.exists(DB):
    setup_db.build()


def clean_sql(t):
    return t.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


def build_system_prompt(hits):
    context = "\n".join(f"- {c['text']}" for _, c in hits)
    return (
        "You are a SQL generator for a SQLite eHospital data warehouse.\n"
        "Use ONLY the tables/columns and DEFINITIONS below. "
        "Return ONLY the SQL query, no markdown, SELECT only.\n\n"
        f"RELEVANT KNOWLEDGE:\n{context}\n"
    )


st.set_page_config(page_title="eHospital AI Query Layer", page_icon="🏥")
st.title("🏥 eHospital — Governed AI Query Layer")
st.caption("Plain-English question → grounded SQL → guardrail-checked → answer. "
           "RAG over your KPI definitions + SQL validation. Runs on SYNTHETIC data — no PHI.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. **Retrieve** the relevant schema + KPI definitions (RAG)\n"
        "2. **Generate** SQL grounded in those definitions\n"
        "3. **Validate** with guardrails (SELECT-only, approved tables)\n"
        "4. **Run** read-only + log every query (audit trail)\n"
    )
    st.markdown(f"**Approved tables:** `{'`, `'.join(APPROVED_TABLES)}`")
    st.info("Try: *weekly cancellation rate* · *billing split by insurance type* · "
            "*top doctors by completed appointments* — or try to break it: *delete all appointments*")

question = st.text_input("Ask about appointments, billing, patients, or blood tests:")

if st.button("Ask") and question.strip():
    if not os.path.exists(DB):
        st.error("Database not found. Run `python setup_db.py` first.")
        st.stop()

    hits = retrieve(question, k=4)
    with st.expander("📚 Retrieved knowledge (what grounded the answer)"):
        for score, c in hits:
            st.write(f"`{score:.2f}` **{c['type']}** — {c['text']}")

    sql = clean_sql(ask(build_system_prompt(hits), question, temperature=0.0)[0])
    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    ok, reason = validate_sql(sql, APPROVED_TABLES)
    if not ok:
        st.error(f"🛑 Blocked by guardrails: {reason}")
        audit_log(question, sql, "BLOCKED", reason)
        st.stop()
    st.success(f"🛡️ Guardrail check passed: {reason}")

    cols, rows, err = run_readonly(DB, sql)
    if err:
        st.error(f"Ran but errored: {err}")
        audit_log(question, sql, "ERROR", err)
    else:
        st.subheader("Result")
        st.dataframe([dict(zip(cols, r)) for r in rows], width="stretch")
        audit_log(question, sql, "RAN", f"{len(rows)} rows")
        st.caption(f"{len(rows)} row(s). Query logged to queries.log.")
