import streamlit as st
from users import users

st.set_page_config(page_title="AutoPost EHR", layout="centered")

st.title("AutoPost EHR")
st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

if st.button("Forgot Password"):
    st.warning("Contact system administrator to reset password")

# Login Logic
if login_btn:
    user_found = False

    for user in users:
        if user["username"] == username and user["password"] == password:
            user_found = True
            st.success(f"Welcome {user['role'].upper()}!")
            st.write(f"You are logged in as: {user['role']}")
            break

    if not user_found:
        st.error("Invalid username or password")