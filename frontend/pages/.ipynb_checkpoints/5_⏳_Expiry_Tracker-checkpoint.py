import streamlit as st
from utils.api import get_pantry
from datetime import datetime

st.title("⏳ Expiry Tracker")

data, code = get_pantry(st.session_state.token)

if code == 200:
    for item in data:
        expiry = item["expiry_date"]
        if expiry:
            exp_date = datetime.strptime(expiry, "%Y-%m-%d")
            days_left = (exp_date - datetime.now()).days

            color = "red" if days_left <= 2 else "orange" if days_left <= 5 else "green"

            st.markdown(
                f"**{item['name']}** — *{item['quantity']} {item['unit']}*  
                **Expiry:** `{expiry}`  
                **Days left:** <span style='color:{color}; font-weight:bold;'>{days_left}</span>",
                unsafe_allow_html=True
            )
            st.write("---")
else:
    st.error("Could not load expiry data.")