import streamlit as st
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
    search = st.text_input("Search by Patient Account # / Invoice # / Patient Name")

    st.write("🔍 Enter value and we will fetch data (next step)")

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