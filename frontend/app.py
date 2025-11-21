import sys
import os

import streamlit as st

# Ensure we can import from utils
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from utils.api import signup, login  # noqa: E402


st.set_page_config(page_title="AppetIte", page_icon="🍳", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

st.title("🍳 AppetIte — Smart AI Recipe Assistant")

# If already logged in, show a quick info and a button to go to Pantry
if st.session_state.token:
    st.info(f"Logged in as **{st.session_state.username}**")
    if st.button("Go to Pantry"):
        st.switch_page("pages/1_Pantry.py")

tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

with tab1:
    st.subheader("Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if not username or not password:
            st.error("Please fill both username and password.")
        else:
            resp = login(username, password)

            if resp["code"] == 200:
                data = resp["data"]
                token = data.get("access_token")

                if not token:
                    st.error("Login succeeded but no token returned from server.")
                else:
                    st.session_state.token = token
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.switch_page("pages/1_Pantry.py")
            else:
                st.error(f"Login failed: {resp['message']}")

with tab2:
    st.subheader("Create Account")

    new_username = st.text_input("Choose a username", key="sign_user")
    email = st.text_input("Email", key="sign_email")
    new_password = st.text_input("Password", type="password", key="sign_pass")

    if st.button("Sign Up"):
        if not new_username or not email or not new_password:
            st.error("Please fill all fields.")
        else:
            resp = signup(new_username, email, new_password)
            if resp["code"] in (200, 201):
                st.success("Account created! Please log in using the Login tab.")
            else:
                st.error(f"Sign up failed: {resp['message']}")