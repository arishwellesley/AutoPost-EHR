import streamlit as st
import pandas as pd
from datetime import date
from modules.data_loader import patients_df, claims_df, payments_df, insurance_df
from users import users

st.set_page_config(page_title="AutoPost EHR", layout="wide")

# =========================
# SESSION
# =========================
if "page" not in st.session_state:
    st.session_state.page = "login"

if "selected_invoice" not in st.session_state:
    st.session_state.selected_invoice = None

if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

# =========================
# LOGIN
# =========================
if st.session_state.page == "login":

    st.title("AutoPost EHR")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        for user in users:
            if user["username"] == username and user["password"] == password:
                st.session_state.page = "dashboard"
                st.session_state.username = username
                st.rerun()

        st.error("Invalid credentials")

# =========================
# DASHBOARD
# =========================
elif st.session_state.page == "dashboard":

    st.title("Dashboard")

    search = st.text_input("Search Patient / Invoice / Name")

    if search:

        search = str(search).strip()

        if search.isdigit() and len(search) == 9:
            st.session_state.selected_patient = search
            st.session_state.page = "invoice_list"
            st.rerun()

        elif search.isdigit():
            result = claims_df[
                claims_df["invoice_number"].astype(str) == search
            ]

            if not result.empty:
                st.session_state.selected_invoice = search
                st.session_state.page = "claim_details"
                st.rerun()
            else:
                st.warning("Invoice not found")

        else:
            result = patients_df[
                patients_df["patient_name"].str.contains(search, case=False, na=False)
            ]
            st.dataframe(result[[
                "patient_name",
                "date_of_birth",
                "patient_account_number"
            ]])

# =========================
# INVOICE LIST
# =========================
elif st.session_state.page == "invoice_list":

    result = claims_df[
        claims_df["patient_account_number"].astype(str)
        == st.session_state.selected_patient
    ]

    st.title("Invoice List")

    for i, row in result.iterrows():

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.write(row["invoice_number"])
        col2.write(row["date_of_service"])
        col3.write(f"${row['billed_amount']:.2f}")
        col4.write(f"${row['outstanding']:.2f}")

        if col5.button("Open", key=i):
            st.session_state.selected_invoice = str(row["invoice_number"])
            st.session_state.page = "claim_details"
            st.rerun()

    if st.button("⬅ Back"):
        st.session_state.page = "dashboard"
        st.rerun()

# =========================
# CLAIM DETAILS
# =========================
elif st.session_state.page == "claim_details":

    invoice = st.session_state.selected_invoice

    claim = claims_df[
        claims_df["invoice_number"].astype(str) == invoice
    ]

    payment = payments_df[
        payments_df["invoice_number"].astype(str) == invoice
    ]

    if not claim.empty:

        row = claim.iloc[0]

        patient = patients_df[
            patients_df["patient_account_number"].astype(str)
            == str(row["patient_account_number"])
        ].iloc[0]

        dob = patient["date_of_birth"]
        age = int((date.today() - dob).days / 365) if pd.notnull(dob) else ""

        left, right = st.columns([3,2])

        with left:
            st.markdown(f"### **{patient['patient_name']}**")
            st.write(f"Phone: {patient.get('phone_number', 'N/A')}")
            st.write(f"DOB: {dob} | Age: {age} | Gender: {patient['gender']}")

        with right:
            st.write(f"Account #: {patient['patient_account_number']}")
            st.write(f"Invoice: {invoice}")
            st.write(f"DOS: {row['date_of_service']}")

        c1, c2 = st.columns(2)
        c1.metric("Billed", f"${row['billed_amount']:.2f}")
        c2.metric("Outstanding", f"${row['outstanding']:.2f}")

        ptr_total = payment[["copay","coinsurance","deductible"]].sum().sum()

        primary_paid = payment[
            payment["payer_code"] == patient["primary_payer_code"]
        ]

        secondary_exists = pd.notnull(patient.get("secondary_payer_name"))

        primary_status = "CLOSED" if not primary_paid.empty else "OPEN"

        secondary_status = "OPEN" if secondary_exists else "CLOSED"

        patient_status = "OPEN" if ptr_total > 0 else "CLOSED"

        st.subheader("Insurance Status")

        col1, col2, col3 = st.columns(3)

        if col1.button(f"Primary - {primary_status}"):
            st.session_state.page = "insurance_details"
            st.session_state.insurance_type = "primary"
            st.rerun()

        if col2.button(f"Secondary - {secondary_status}"):
            st.session_state.page = "insurance_details"
            st.session_state.insurance_type = "secondary"
            st.rerun()

        if col3.button(f"Patient - {patient_status}"):
            st.session_state.page = "insurance_details"
            st.session_state.insurance_type = "patient"
            st.rerun()

        st.subheader("Provider Info")

        st.write(f"Doctor: {row.get('rendering_provider_name')} (NPI: {row.get('rendering_provider_npi')})")
        st.write(f"Facility: {row.get('facility_name')} (NPI: {row.get('facility_npi')})")

        st.subheader("Payments")

        st.dataframe(payment, use_container_width=True)

        if st.button("💳 Payment Posting"):
            st.session_state.page = "payment_posting"
            st.rerun()

        if st.button("⬅ Back"):
            st.session_state.page = "invoice_list"
            st.rerun()

# =========================
# INSURANCE DETAILS PAGE
# =========================
elif st.session_state.page == "insurance_details":

    st.title("Insurance Details")

    invoice = st.session_state.selected_invoice

    claim = claims_df[
        claims_df["invoice_number"].astype(str) == invoice
    ].iloc[0]

    patient = patients_df[
        patients_df["patient_account_number"].astype(str)
        == str(claim["patient_account_number"])
    ].iloc[0]

    ins_type = st.session_state.insurance_type

    if ins_type == "primary":
        payer_code = patient["primary_payer_code"]
        member_id = patient["primary_member_number"]
        eff = patient["primary_effective_date"]
        term = patient["primary_termination_date"]

    else:
        payer_code = patient.get("secondary_payer_code")
        member_id = patient.get("secondary_member_number")
        eff = patient.get("secondary_effective_date")
        term = patient.get("secondary_termination_date")

    ins = insurance_df[
        insurance_df["payer_code"] == payer_code
    ]

    if not ins.empty:
        ins_row = ins.iloc[0]

        st.write(f"Payer Code: {payer_code}")
        st.write(f"Payer Name: {ins_row['payer_name']}")
        st.write(f"Plan Type: {ins_row['plan_type']}")
        st.write(f"Member ID: {member_id}")
        st.write(f"Payer Type: {ins_row['payer_type']}")
        st.write(f"Payer ID: {ins_row['payer_id']}")
        st.write(f"{ins_row['mailing_address_line1']}")
        st.write(f"{ins_row['city']} {ins_row['state']} {ins_row['zip_code']}")
        st.write(f"Phone: {ins_row['phone_number']}")
        st.write(f"Effective: {eff}")
        st.write(f"Termination: {term}")

    if st.button("⬅ Back"):
        st.session_state.page = "claim_details"
        st.rerun()