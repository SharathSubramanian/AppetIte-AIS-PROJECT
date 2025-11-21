# frontend/app.py

from __future__ import annotations

import streamlit as st

from utils.api import signup, login

st.set_page_config(page_title="AppetIte", page_icon="🍽", layout="centered")

st.title("🍽 AppetIte – Smart Recipe Assistant")

# Session state: token and username
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "mode" not in st.session_state:
    st.session_state["mode"] = "login"

mode = st.radio("Choose mode", ["Login", "Sign up"], horizontal=True)
st.session_state["mode"] = "login" if mode == "Login" else "signup"

# ---------------------------------------------------------
# Signup
# ---------------------------------------------------------
if st.session_state["mode"] == "signup":
    st.subheader("Create a new account")

    su_username = st.text_input("Username")
    su_email = st.text_input("Email")
    su_password = st.text_input("Password", type="password")

    if st.button("Sign up"):
        if not (su_username and su_email and su_password):
            st.error("Please fill in all fields.")
        else:
            resp = signup(su_username, su_email, su_password)
            if resp["code"] != 201:
                st.error(f"Sign up failed ({resp['code']}): {resp['message']}")
            else:
                st.success("Account created. You can now log in.")

# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
else:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not (username and password):
            st.error("Please enter username and password.")
        else:
            resp = login(username, password)
            if resp["code"] != 200 or not resp["data"] or "access_token" not in resp["data"]:
                st.error(f"Login failed ({resp['code']}): {resp['message']}")
            else:
                token = resp["data"]["access_token"]
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.success("Logged in successfully. Use the sidebar to navigate.")