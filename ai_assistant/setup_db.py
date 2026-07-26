"""
setup_db.py — builds a SYNTHETIC eHospital warehouse as a local SQLite file.

Why SQLite + fake data?
  - Real hospital data is PHI (protected health info). It must NEVER go on GitHub.
  - SQLite needs no server, so anyone can clone the repo and run the demo instantly.
  - The tables mirror your real MySQL warehouse (EHOSPITAL_DW) 1:1, including the
    stored `year_week` column, so the KPI SQL is identical to your production logic.

Tables (same shape as your dw/00_create_dw_schema.sql):
  dim_patient, fact_appointments, fact_billing, fact_bloodtests

Run:  python setup_db.py   ->  creates ehospital_dw.db
"""
import os
import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)  # deterministic: same data every run

DB = os.path.join(os.path.dirname(__file__), "ehospital_dw.db")


def year_week(d):
    """Integer YYYYWW, matching MySQL YEARWEEK(dt, 1) closely (ISO week)."""
    iso = d.isocalendar()  # (year, week, weekday)
    return iso[0] * 100 + iso[1]


def build():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    c = con.cursor()

    # ---- schema (mirrors EHOSPITAL_DW) ----
    c.executescript("""
    CREATE TABLE dim_patient (
      patient_id INTEGER PRIMARY KEY,
      name TEXT, dob DATE, gender TEXT, phone_number TEXT,
      OHIP_code TEXT, private_insurance_name TEXT, private_insurance_id TEXT,
      weight_kg REAL, height_cm REAL, family_doctor_id INTEGER
    );
    CREATE TABLE fact_appointments (
      appointment_id INTEGER PRIMARY KEY,
      patient_id INTEGER NOT NULL,
      doctor_id INTEGER,
      appointment_dt TEXT NOT NULL,
      status TEXT,
      year_week INTEGER
    );
    CREATE TABLE fact_billing (
      billing_id INTEGER PRIMARY KEY,
      appointment_id INTEGER,
      patient_id INTEGER NOT NULL,
      amount REAL,
      billing_date DATE NOT NULL,
      billing_status TEXT,
      bill_type TEXT,
      year_week INTEGER
    );
    CREATE TABLE fact_bloodtests (
      bloodtest_id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_id INTEGER NOT NULL,
      test_name TEXT NOT NULL,
      result_value TEXT, unit TEXT, normal_range TEXT,
      test_date DATE NOT NULL,
      year_week INTEGER
    );
    """)

    # ---- reference values ----
    first = ["Aisha","Liam","Noah","Priya","Wei","Fatima","Diego","Sofia","Omar","Emma",
             "Raj","Chloe","Ivan","Mei","Kwame","Sara","Tom","Nina","Hassan","Grace"]
    last = ["Singh","Chen","Patel","Nguyen","Garcia","Khan","Brown","Kim","Ali","Wilson",
            "Rossi","Silva","Haddad","Osei","Dubois","Cohen","Ivanov","Tran","Lopez","Park"]
    genders = ["Female", "Male", "Other"]
    ins_names = ["Sun Life", "Manulife", "Canada Life", "Green Shield"]
    doctors = list(range(101, 113))  # 12 doctors
    appt_status = (["Completed"] * 62 + ["Cancelled"] * 14 +
                   ["No-Show"] * 9 + ["Scheduled"] * 15)  # realistic mix
    bill_status = ["Paid", "Pending", "Denied"]
    bill_types = ["Consultation", "Procedure", "Lab", "Imaging"]
    tests = [
        ("Complete Blood Count", "x10^9/L", "4.0-11.0"),
        ("Lipid Panel", "mmol/L", "0.0-5.2"),
        ("HbA1c", "%", "4.0-5.6"),
        ("TSH", "mIU/L", "0.4-4.0"),
        ("Vitamin D", "nmol/L", "75-250"),
        ("Ferritin", "ug/L", "30-400"),
        ("Creatinine", "umol/L", "60-110"),
        ("ALT", "U/L", "7-56"),
    ]

    # ---- dim_patient (200 patients) ----
    patients = []
    for pid in range(1, 201):
        name = f"{random.choice(first)} {random.choice(last)}"
        dob = (datetime(1950, 1, 1) + timedelta(days=random.randint(0, 26000))).date().isoformat()
        # ~65% OHIP-only, ~30% private, ~5% unknown
        roll = random.random()
        ohip = f"OHIP{random.randint(1000000000, 9999999999)}" if roll < 0.95 else ""
        if roll >= 0.65:  # some of them ALSO have private
            pin = f"PRIV{random.randint(100000, 999999)}"
            pname = random.choice(ins_names)
        else:
            pin, pname = "", ""
        patients.append((
            pid, name, dob, random.choice(genders), f"613555{random.randint(1000,9999)}",
            ohip, pname, pin,
            round(random.uniform(50, 110), 1), round(random.uniform(150, 195), 1),
            random.choice(doctors),
        ))
    c.executemany("INSERT INTO dim_patient VALUES (?,?,?,?,?,?,?,?,?,?,?)", patients)

    # ---- fact_appointments (2,000 over 26 weeks of 2025) ----
    start = datetime(2025, 1, 6, 8, 0)  # a Monday
    appts = []
    for aid in range(1, 2001):
        pid = random.randint(1, 200)
        dt = start + timedelta(days=random.randint(0, 181),
                               hours=random.randint(0, 9), minutes=random.choice([0, 15, 30, 45]))
        status = random.choice(appt_status)
        appts.append((aid, pid, random.choice(doctors), dt.isoformat(sep=" "),
                      status, year_week(dt)))
    c.executemany("INSERT INTO fact_appointments VALUES (?,?,?,?,?,?)", appts)

    # ---- fact_billing (one bill per Completed appt) ----
    bills = []
    bid = 1
    for aid, pid, doc, dt_s, status, yw in appts:
        if status != "Completed":
            continue
        dt = datetime.fromisoformat(dt_s)
        btype = random.choice(bill_types)
        base = {"Consultation": 90, "Procedure": 480, "Lab": 55, "Imaging": 260}[btype]
        amount = round(base * random.uniform(0.8, 1.6), 2)
        bstatus = random.choices(bill_status, weights=[70, 22, 8])[0]
        bdate = (dt + timedelta(days=random.randint(0, 5))).date().isoformat()
        bills.append((bid, aid, pid, amount, bdate, bstatus, btype, year_week(dt)))
        bid += 1
    c.executemany("INSERT INTO fact_billing VALUES (?,?,?,?,?,?,?,?)", bills)

    # ---- fact_bloodtests (~1,500) ----
    bts = []
    for _ in range(1500):
        pid = random.randint(1, 200)
        tname, unit, nrange = random.choice(tests)
        dt = start + timedelta(days=random.randint(0, 181))
        val = round(random.uniform(0.5, 12.0), 1)
        bts.append((pid, tname, str(val), unit, nrange, dt.date().isoformat(), year_week(dt)))
    c.executemany(
        "INSERT INTO fact_bloodtests (patient_id,test_name,result_value,unit,normal_range,test_date,year_week) "
        "VALUES (?,?,?,?,?,?,?)", bts)

    con.commit()

    # ---- quick summary ----
    for t in ["dim_patient", "fact_appointments", "fact_billing", "fact_bloodtests"]:
        n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:20} {n:>6} rows")
    con.close()
    print(f"\nCreated {DB}")
    print("Synthetic data only — no real patient information.")


if __name__ == "__main__":
    build()
