# frontend/app.py

from __future__ import annotations

import streamlit as st

from utils.api import signup, login


st.set_page_config(
    page_title="AppetIte",
    page_icon="🍽️",
    layout="centered",
)

# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "token" not in st.session_state:
    st.session_state["token"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

st.title("🍽️ AppetIte – Smart Recipe Assistant")

if st.session_state["token"]:
    st.success(f"Logged in as **{st.session_state['username']}**")
else:
    st.info("Please log in or sign up to use your pantry and recipes.")

mode = st.radio("Choose mode", ["Login", "Sign up"], horizontal=True)

# ---------------------- LOGIN ---------------------- #
if mode == "Login":
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            resp = login(username, password)

            # Expecting resp = {"code": int, "data": dict|None, "message": str}
            data = resp.get("data") or {}

            if (
                resp["code"] != 200
                or not isinstance(data, dict)
                or "access_token" not in data
            ):
                st.error(f"Login failed ({resp['code']}): {resp.get('message', 'unknown error')}")
            else:
                token = data["access_token"]
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.success("Login successful! You can now use the other pages.")

# ---------------------- SIGNUP ---------------------- #
else:
    st.subheader("Sign up")

    su_username = st.text_input("Username", key="signup_username")
    su_email = st.text_input("Email", key="signup_email")
    su_password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create account"):
        if not su_username or not su_email or not su_password:
            st.error("Please fill in username, email, and password.")
        else:
            resp = signup(su_username, su_email, su_password)
            if resp["code"] != 201:
                st.error(f"Sign up failed ({resp['code']}): {resp.get('message', '')}")
            else:
                st.success("Account created successfully! You can now switch to Login.")