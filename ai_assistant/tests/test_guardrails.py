"""
Unit tests for guardrails.py — the safety layer in front of the AI text-to-SQL.

Run from the ai_assistant/ folder:   pytest -q
No API key is needed: these tests exercise validate_sql() and run_readonly() only.
"""
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from guardrails import validate_sql, run_readonly  # noqa: E402

APPROVED = ["dim_patient", "fact_appointments", "fact_billing", "fact_bloodtests"]


# ---------- queries that must be ALLOWED ----------
@pytest.mark.parametrize("sql", [
    "SELECT year_week, COUNT(*) FROM fact_appointments GROUP BY year_week",
    "WITH c AS (SELECT * FROM fact_billing) SELECT COUNT(*) FROM c",
    "SELECT b.billing_status, SUM(b.amount) FROM fact_billing b "
    "JOIN dim_patient p ON p.patient_id = b.patient_id GROUP BY b.billing_status",
    "SELECT patient_id FROM dim_patient UNION SELECT patient_id FROM fact_billing",
])
def test_safe_selects_are_allowed(sql):
    ok, reason = validate_sql(sql, APPROVED)
    assert ok, reason


# ---------- queries that must be BLOCKED ----------
@pytest.mark.parametrize("sql, expected_reason", [
    ("DROP TABLE fact_billing", "Only SELECT"),
    ("DELETE FROM fact_appointments", "Only SELECT"),
    ("UPDATE fact_billing SET amount = 0", "Only SELECT"),
    ("INSERT INTO dim_patient VALUES (1)", "Only SELECT"),
    ("SELECT 1; DROP TABLE dim_patient", "Multiple statements"),
    ("SELECT * FROM staff_salaries", "non-approved tables"),
    ("SELECT * FROM fact_billing JOIN staff_salaries s ON 1=1", "non-approved tables"),
    ("", "No SQL statement"),
])
def test_unsafe_queries_are_blocked(sql, expected_reason):
    ok, reason = validate_sql(sql, APPROVED)
    assert not ok
    assert expected_reason in reason


# ---------- read-only execution ----------
@pytest.fixture
def tiny_db(tmp_path):
    db = tmp_path / "tiny.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE fact_billing (billing_id INT, amount REAL)")
    con.executemany("INSERT INTO fact_billing VALUES (?, ?)", [(1, 100.0), (2, 50.0)])
    con.commit()
    con.close()
    return str(db)


def test_run_readonly_returns_rows(tiny_db):
    cols, rows, err = run_readonly(tiny_db, "SELECT SUM(amount) AS total FROM fact_billing")
    assert err is None
    assert cols == ["total"]
    assert rows == [(150.0,)]


def test_run_readonly_cannot_write_even_if_validation_is_bypassed(tiny_db):
    # Belt and suspenders: the connection itself is read-only.
    cols, rows, err = run_readonly(tiny_db, "DELETE FROM fact_billing")
    assert err is not None
    con = sqlite3.connect(tiny_db)
    assert con.execute("SELECT COUNT(*) FROM fact_billing").fetchone()[0] == 2
    con.close()
