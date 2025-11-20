import streamlit as st
from utils.api import signup, login

st.set_page_config(page_title="AppetIte", page_icon="🍳", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None

st.title("🍳 AppetIte — Smart AI Recipe Assistant")

tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

with tab1:
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        data, code = login(username, password)
        if code == 200:
            st.session_state.token = data["access_token"]
            st.success("Logged in successfully!")
            st.switch_page("pages/1_Pantry.py")
        else:
            st.error("Invalid username or password.")

with tab2:
    st.subheader("Create Account")
    username = st.text_input("Choose a username", key="sign_user")
    email = st.text_input("Email", key="sign_email")
    password = st.text_input("Password", type="password", key="sign_pass")

    if st.button("Sign Up"):
        data, code = signup(username, email, password)
        if code in (200, 201):
            st.success("Account created! Please log in.")
        else:
            st.error("Username already exists.")