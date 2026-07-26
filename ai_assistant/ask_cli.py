"""
ask_cli.py — terminal version of the assistant (no browser needed).
Run:  python ask_cli.py
Ask questions in plain English; type 'quit' to exit.
Great for a quick demo or for testing the full RAG -> generate -> guardrail -> run loop.
"""
import os
from llm import ask
from rag import retrieve
from guardrails import validate_sql, run_readonly, audit_log

DB = os.path.join(os.path.dirname(__file__), "ehospital_dw.db")
APPROVED_TABLES = ["dim_patient", "fact_appointments", "fact_billing", "fact_bloodtests"]


def clean_sql(t):
    return t.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


def build_system_prompt(hits):
    context = "\n".join(f"- {c['text']}" for _, c in hits)
    return ("You are a SQL generator for a SQLite eHospital data warehouse.\n"
            "Use ONLY the tables/columns and DEFINITIONS below. "
            "Return ONLY the SQL query, no markdown, SELECT only.\n\n"
            f"RELEVANT KNOWLEDGE:\n{context}\n")


if __name__ == "__main__":
    if not os.path.exists(DB):
        raise SystemExit("Database not found. Run `python setup_db.py` first.")

    print("Guarded eHospital assistant ready. Ask a question (or 'quit').")
    print("Try:  weekly cancellation rate  /  billing split by insurance type")
    print("Break it:  delete all appointments\n")

    while True:
        q = input("Q> ").strip()
        if q.lower() in {"quit", "exit"}:
            break
        if not q:
            continue

        hits = retrieve(q, k=4)
        sql = clean_sql(ask(build_system_prompt(hits), q, temperature=0.0)[0])
        print("\nGenerated SQL:\n", sql)

        ok, reason = validate_sql(sql, APPROVED_TABLES)
        if not ok:
            print(f"\n🛑 BLOCKED before running: {reason}\n")
            audit_log(q, sql, "BLOCKED", reason)
            continue
        print(f"\n🛡️  Guardrail check: {reason}")

        cols, rows, err = run_readonly(DB, sql)
        if err:
            print(f"Ran but errored: {err}\n")
            audit_log(q, sql, "ERROR", err)
        else:
            print("✅ Result. Columns:", cols)
            for r in rows[:10]:
                print("  ", r)
            if len(rows) > 10:
                print(f"   ... ({len(rows)} rows total)")
            audit_log(q, sql, "RAN", f"{len(rows)} rows")
        print()

    print("Every attempt was logged to queries.log — your audit trail.")
