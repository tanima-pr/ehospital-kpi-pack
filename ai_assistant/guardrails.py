"""
guardrails.py — the safety layer that makes AI-generated SQL trustworthy.

Never run raw SQL from an AI. First pass it through validate_sql(), which checks:
  1. Is it even valid SQL?          (parse it)
  2. Is it a single statement?      (block "SELECT 1; DROP TABLE ..." injection)
  3. Is it read-only?               (block DROP/DELETE/UPDATE/INSERT/ALTER/etc.)
  4. Does it only touch approved tables?

Then we run it on a READ-ONLY connection, so even if something slipped past,
the database physically cannot be changed. Belt and suspenders — exactly the kind
of governance a healthcare data platform needs.
"""
import sqlite3, datetime, os
import sqlglot
from sqlglot import exp

# Operations that must NEVER appear in an analyst's read query.
FORBIDDEN_NODES = (
    exp.Insert, exp.Update, exp.Delete, exp.Drop,
    exp.Create, exp.Alter, exp.Command,   # Command catches TRUNCATE, PRAGMA, GRANT...
)

LOG_FILE = os.path.join(os.path.dirname(__file__), "queries.log")


def validate_sql(sql, allowed_tables):
    """Return (ok: bool, reason: str). ok=True means safe to run."""
    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except Exception as e:
        return False, f"Could not parse as valid SQL: {e}"

    if len(statements) == 0:
        return False, "No SQL statement found."
    if len(statements) > 1:
        return False, "Multiple statements are not allowed (possible injection)."

    stmt = statements[0]

    if not isinstance(stmt, (exp.Select, exp.Union)):
        return False, f"Only SELECT queries are allowed (got {type(stmt).__name__})."
    for node_type in FORBIDDEN_NODES:
        if list(stmt.find_all(node_type)):
            return False, f"Forbidden operation detected: {node_type.__name__.upper()}"

    # Only approved tables (exclude CTE names like "WITH x AS (...)").
    cte_names = {cte.alias_or_name for cte in stmt.find_all(exp.CTE)}
    used = {t.name for t in stmt.find_all(exp.Table)} - cte_names
    not_allowed = used - set(allowed_tables)
    if not_allowed:
        return False, f"Query uses non-approved tables: {sorted(not_allowed)}"

    return True, "OK — safe SELECT on approved tables."


def run_readonly(db, sql):
    """Run SQL on a READ-ONLY connection. Writes are impossible here."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)  # mode=ro is the key
    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        return cols, cur.fetchall(), None
    except Exception as e:
        return None, None, str(e)
    finally:
        con.close()


def audit_log(question, sql, verdict, note=""):
    """Append every attempt to queries.log — an audit trail (vital for healthcare)."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts}\tQ={question!r}\tVERDICT={verdict}\tNOTE={note}\tSQL={sql!r}\n")


if __name__ == "__main__":
    # Mini self-test — no API key needed. Uses the hospital tables.
    APPROVED = ["dim_patient", "fact_appointments", "fact_billing", "fact_bloodtests"]
    tests = [
        ("SELECT year_week, COUNT(*) FROM fact_appointments GROUP BY year_week", "should PASS"),
        ("DROP TABLE fact_billing", "should BLOCK"),
        ("DELETE FROM fact_appointments", "should BLOCK"),
        ("UPDATE fact_billing SET amount=0", "should BLOCK"),
        ("SELECT 1; DROP TABLE dim_patient", "should BLOCK (injection)"),
        ("SELECT * FROM staff_salaries", "should BLOCK (not approved)"),
        ("WITH c AS (SELECT * FROM fact_billing) SELECT COUNT(*) FROM c", "should PASS (CTE)"),
        ("SELECT b.billing_status, SUM(b.amount) FROM fact_billing b "
         "JOIN dim_patient p ON p.patient_id=b.patient_id GROUP BY b.billing_status", "should PASS"),
    ]
    for sql, expect in tests:
        ok, reason = validate_sql(sql, APPROVED)
        mark = "PASS " if ok else "BLOCK"
        print(f"[{mark}] {expect:28} | {reason}")
