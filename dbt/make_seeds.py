"""
make_seeds.py — generates the RAW synthetic eHospital data as CSV files in seeds/.

In analytics engineering, "raw" data is messy and untransformed — dbt's job is to
clean and model it. So these CSVs deliberately hold ONLY raw columns (no year_week,
no derived insurance_type). dbt computes all of that downstream.

You normally won't need to run this — the CSVs are already in seeds/. It's here so
you can see exactly how the synthetic (fake, no PHI) data was produced.

Run:  python make_seeds.py   ->  writes seeds/raw_*.csv
"""
import csv, os, random
from datetime import datetime, timedelta

random.seed(42)
SEEDS = os.path.join(os.path.dirname(__file__), "seeds")
os.makedirs(SEEDS, exist_ok=True)


def write(name, header, rows):
    path = os.path.join(SEEDS, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  seeds/{name:24} {len(rows):>5} rows")


first = ["Aisha","Liam","Noah","Priya","Wei","Fatima","Diego","Sofia","Omar","Emma",
         "Raj","Chloe","Ivan","Mei","Kwame","Sara","Tom","Nina","Hassan","Grace"]
last = ["Singh","Chen","Patel","Nguyen","Garcia","Khan","Brown","Kim","Ali","Wilson",
        "Rossi","Silva","Haddad","Osei","Dubois","Cohen","Ivanov","Tran","Lopez","Park"]
genders = ["Female", "Male", "Other"]
ins_names = ["Sun Life", "Manulife", "Canada Life", "Green Shield"]
doctors = list(range(101, 113))
appt_status = ["Completed"]*62 + ["Cancelled"]*14 + ["No-Show"]*9 + ["Scheduled"]*15
bill_status = ["Paid", "Pending", "Denied"]
bill_types = ["Consultation", "Procedure", "Lab", "Imaging"]
tests = ["Complete Blood Count","Lipid Panel","HbA1c","TSH","Vitamin D","Ferritin","Creatinine","ALT"]

# ---- patients ----
patients = []
for pid in range(1, 201):
    dob = (datetime(1950,1,1) + timedelta(days=random.randint(0,26000))).date().isoformat()
    roll = random.random()
    ohip = f"OHIP{random.randint(1000000000,9999999999)}" if roll < 0.95 else ""
    if roll >= 0.65:
        pin, pname = f"PRIV{random.randint(100000,999999)}", random.choice(ins_names)
    else:
        pin, pname = "", ""
    patients.append([pid, f"{random.choice(first)} {random.choice(last)}", dob,
                     random.choice(genders), ohip, pname, pin, random.choice(doctors)])
write("raw_patients.csv",
      ["patient_id","name","dob","gender","ohip_code","private_insurance_name",
       "private_insurance_id","family_doctor_id"], patients)

# ---- appointments (raw: datetime + status only) ----
start = datetime(2025,1,6,8,0)
appts = []
for aid in range(1, 2001):
    dt = start + timedelta(days=random.randint(0,181), hours=random.randint(0,9),
                           minutes=random.choice([0,15,30,45]))
    appts.append([aid, random.randint(1,200), random.choice(doctors),
                  dt.isoformat(sep=" "), random.choice(appt_status)])
write("raw_appointments.csv",
      ["appointment_id","patient_id","doctor_id","appointment_dt","status"], appts)

# ---- billing (one per Completed appt) ----
bills, bid = [], 1
for aid, pid, doc, dt_s, status in appts:
    if status != "Completed":
        continue
    dt = datetime.fromisoformat(dt_s)
    btype = random.choice(bill_types)
    base = {"Consultation":90,"Procedure":480,"Lab":55,"Imaging":260}[btype]
    amount = round(base * random.uniform(0.8,1.6), 2)
    bstatus = random.choices(bill_status, weights=[70,22,8])[0]
    bdate = (dt + timedelta(days=random.randint(0,5))).date().isoformat()
    bills.append([bid, aid, pid, amount, bdate, bstatus, btype]); bid += 1
write("raw_billing.csv",
      ["billing_id","appointment_id","patient_id","amount","billing_date",
       "billing_status","bill_type"], bills)

# ---- bloodtests ----
bts = []
for i in range(1, 1501):
    dt = start + timedelta(days=random.randint(0,181))
    bts.append([i, random.randint(1,200), random.choice(tests), dt.date().isoformat()])
write("raw_bloodtests.csv", ["bloodtest_id","patient_id","test_name","test_date"], bts)

print("\nRaw synthetic seeds written to seeds/. No real patient data.")
