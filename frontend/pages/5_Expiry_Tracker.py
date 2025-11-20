# frontend/pages/5_Expiry_Tracker.py

import streamlit as st

from utils.api import get_expiring_items

st.title("⏳ Expiry Tracker")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in from the main page first.")
    st.stop()

st.write(
    "Track which pantry items are expiring soon so you can prioritize using them."
)

days = st.slider("Show items expiring in the next (days)", min_value=1, max_value=30, value=7)

if st.button("🔍 Check expiring items"):
    data, code = get_expiring_items(token, days=days)
    if code == 200 and isinstance(data, list):
        if not data:
            st.success(f"No items expiring in the next {days} days. Nice job!")
        else:
            st.subheader("Items expiring soon")
            for item in data:
                name = item.get("name", "Unknown")
                quantity = item.get("quantity", "?")
                unit = item.get("unit", "")
                expiry_date = item.get("expiry_date", "N/A")
                st.write(
                    f"**{name}** — *{quantity} {unit}*  "
                    f"(expires on `{expiry_date}`)"
                )
    else:
        st.error(f"Could not fetch expiring items: {data}")