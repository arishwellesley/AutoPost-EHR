import streamlit as st

st.set_page_config(page_title="AutoPost EHR", layout="centered")

# Title
st.title("AutoPost EHR")

# Login Box
st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

# Forgot Password
if st.button("Forgot Password"):
    st.warning("Contact system administrator to reset password")

# Login Logic (Temporary)
if login_btn:
    if username == "admin" and password == "admin123":
        st.success("Login successful")
    else:
        st.error("Invalid username or password")