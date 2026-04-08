import pandas as pd

# =========================
# LOAD DATA
# =========================
patients_df = pd.read_excel("Data/patients.xlsx")
claims_df = pd.read_excel("Data/claims.xlsx")
payments_df = pd.read_excel("Data/payments.xlsx")
providers_df = pd.read_excel("Data/providers.xlsx")
insurance_df = pd.read_excel("Data/payers.xlsx")

# =========================
# CLEAN COLUMN NAMES
# =========================
for df in [patients_df, claims_df, payments_df, providers_df, insurance_df]:
    df.columns = df.columns.str.strip().str.lower()

# =========================
# DATE FORMATTING
# =========================
date_cols = [
    "date_of_birth",
    "primary_effective_date",
    "primary_termination_date",
    "secondary_effective_date",
    "secondary_termination_date"
]

for col in date_cols:
    if col in patients_df.columns:
        patients_df[col] = pd.to_datetime(patients_df[col], errors="coerce").dt.date

if "date_of_service" in claims_df.columns:
    claims_df["date_of_service"] = pd.to_datetime(
        claims_df["date_of_service"], errors="coerce"
    ).dt.date

if "paid_date" in payments_df.columns:
    payments_df["paid_date"] = pd.to_datetime(
        payments_df["paid_date"], errors="coerce"
    ).dt.date

# =========================
# PROVIDER MAPPING
# =========================
provider_lookup = {}

if "provider_npi" in providers_df.columns and "provider_full_name" in providers_df.columns:
    provider_lookup = providers_df.set_index("provider_npi")["provider_full_name"].to_dict()

if "rendering_provider_npi" in claims_df.columns:
    claims_df["rendering_provider_name"] = claims_df["rendering_provider_npi"].map(provider_lookup)

if "facility_npi" in claims_df.columns:
    claims_df["facility_name"] = claims_df["facility_npi"].map(provider_lookup)

# =========================
# PTR COLUMNS
# =========================
for col in ["copay", "coinsurance", "deductible"]:
    if col not in payments_df.columns:
        payments_df[col] = 0

# =========================
# RENAME ADJUSTMENT
# =========================
if "contractual_adjustment" in payments_df.columns:
    payments_df = payments_df.rename(columns={
        "contractual_adjustment": "adjustment"
    })

# =========================
# AGGREGATE PAYMENTS
# =========================
payment_summary = payments_df.groupby("invoice_number").agg({
    "paid_amount": "sum",
    "adjustment": "sum",
    "copay": "sum",
    "coinsurance": "sum",
    "deductible": "sum"
}).reset_index()

# =========================
# MERGE CLAIMS + PAYMENTS
# =========================
claims_df = claims_df.merge(payment_summary, on="invoice_number", how="left")

# =========================
# FILL NULLS
# =========================
for col in ["paid_amount", "adjustment", "copay", "coinsurance", "deductible"]:
    claims_df[col] = claims_df[col].fillna(0)

# =========================
# OUTSTANDING
# =========================
claims_df["outstanding"] = (
    claims_df["billed_amount"]
    - (
        claims_df["paid_amount"]
        + claims_df["adjustment"]
        + claims_df["copay"]
        + claims_df["coinsurance"]
        + claims_df["deductible"]
    )
)

claims_df["outstanding"] = claims_df["outstanding"].round(2)