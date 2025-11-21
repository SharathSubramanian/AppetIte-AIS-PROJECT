from datetime import date, datetime
from typing import List, Dict, Any

import streamlit as st

from utils.api import get_pantry


st.set_page_config(page_title="Expiry Tracker", page_icon="⏰", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("⏰ Expiry Tracker")

resp = get_pantry(token)
if resp["code"] != 200:
    st.error(f"Could not load pantry: {resp['message']}")
    st.stop()

items: List[Dict[str, Any]] = resp["data"] or []

today = date.today()
exp_items: List[Dict[str, Any]] = []

for item in items:
    exp_str = item.get("expiry_date")
    if not exp_str:
        continue
    try:
        exp_date = datetime.fromisoformat(exp_str).date()
    except Exception:
        # If parsing fails, skip this item
        continue
    days_left = (exp_date - today).days
    item_copy = dict(item)
    item_copy["days_left"] = days_left
    exp_items.append(item_copy)

if not exp_items:
    st.info("No expiry information found. Add expiry dates when you create pantry items.")
else:
    # Sort by soonest expiry
    exp_items.sort(key=lambda x: x["days_left"])

    st.subheader("Items nearing expiry")

    for item in exp_items:
        name = item.get("name", "")
        qty = item.get("quantity", "")
        unit = item.get("unit", "")
        days_left = item["days_left"]

        if days_left < 0:
            label = "Expired"
            color = "🚨"
        elif days_left == 0:
            label = "Expires today"
            color = "⚠️"
        elif days_left <= 3:
            label = f"Expires in {days_left} day(s)"
            color = "⚠️"
        else:
            label = f"Expires in {days_left} day(s)"
            color = "✅"

        st.markdown(
            f"{color} **{name}** — *{qty} {unit}*  \n"
            f"&nbsp;&nbsp;&nbsp;&nbsp;{label}"
        )