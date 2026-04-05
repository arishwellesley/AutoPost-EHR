
import streamlit as st
from modules.data_loader import patients_df, claims_df
from users import users

st.set_page_config(page_title="AutoPost EHR", layout="wide")

# SESSION INIT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# LOGIN PAGE
if not st.session_state.logged_in:

    st.title("AutoPost EHR")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_btn = st.button("Login")

    if st.button("Forgot Password"):
        st.warning("Contact system administrator to reset password")

    if login_btn:
        for user in users:
            if user["username"] == username and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = user["role"]
                st.session_state.username = user["username"]
                st.rerun()

        st.error("Invalid username or password")

# DASHBOARD
else:
    st.title("AutoPost EHR Dashboard")

    col1, col2 = st.columns([8, 2])

    with col1:
        st.write(f"Welcome, {st.session_state.username} ({st.session_state.role})")

    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()

    # SEARCH BAR
    st.markdown("## 🔍 Patient Search")

search = st.text_input("Enter Patient Account # / Invoice # / Patient Name")

st.markdown("### 🔎 Patient / Claim Search")
st.markdown("---")

search = st.text_input("", placeholder="Enter Patient Account # / Invoice # / Name")


if search:

    # CASE 1 — Patient Account #
    if search.isdigit() and len(search) == 9:
        result = claims_df[claims_df["patient_account_number"] == int(search)]

        if not result.empty:
            st.subheader("Invoices for Patient")

            display = result[["invoice_number", "date_of_service", "billed_amount"]]
            st.dataframe(display)
        else:
            st.warning("No records found")

    # CASE 2 — Invoice #
    elif search.isdigit():
        result = claims_df[claims_df["invoice_number"] == int(search)]

        if not result.empty:
            st.success("Invoice found")
            st.dataframe(result)
        else:
            st.warning("Invoice not found")

    # CASE 3 — Patient Name
    else:
        result = patients_df[patients_df["patient_name"].str.contains(search, case=False)]

        if not result.empty:
            st.subheader("Matching Patients")

            display = result[[
                "patient_name",
                "date_of_birth",
                "patient_account_number",
                "primary_member_number"
            ]]

            st.dataframe(display)
        else:
            st.warning("No patients found")

    st.divider()

    # PLACEHOLDER SECTIONS
    st.subheader("Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Patient Lookup")

    with col2:
        st.info("Claims")

    with col3:
        st.info("Payments")