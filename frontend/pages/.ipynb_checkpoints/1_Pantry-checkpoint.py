# frontend/pages/1_Pantry.py

from typing import Any, Dict, List, Optional

import streamlit as st

from utils.api import add_pantry, get_pantry, delete_pantry_item

st.set_page_config(page_title="Pantry", page_icon="🧺", layout="wide")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🧺 Your Pantry")

with st.form("add_pantry_form", clear_on_submit=True):
    cols = st.columns(4)
    name = cols[0].text_input("Item name")
    category = cols[1].selectbox(
        "Category",
        ["vegetable", "fruit", "protein", "carb", "spice", "other"],
    )
    quantity = cols[2].number_input("Quantity", min_value=0.0, value=1.0, step=1.0)
    unit = cols[3].text_input("Unit", value="pcs")

    expiry_date = st.date_input(
        "Expiry date (optional)",
        value=None,
        format="YYYY-MM-DD",
    )

    submitted = st.form_submit_button("Add to pantry")

    if submitted:
        if not name.strip():
            st.error("Please enter a name.")
        else:
            expiry_str: Optional[str] = None
            if expiry_date:
                expiry_str = expiry_date.isoformat()

            resp = add_pantry(
                token,
                name=name.strip(),
                category=category,
                quantity=quantity,
                unit=unit.strip(),
                expiry_date=expiry_str,
            )
            if resp["code"] >= 400:
                st.error(f"Failed to add item: {resp['message']}")
            else:
                st.success("Item added to pantry.")
                st.rerun()

# Fetch pantry items
resp = get_pantry(token)
if resp["code"] >= 400:
    st.error(f"Failed to load pantry: {resp['message']}")
    st.stop()

items: List[Dict[str, Any]] = resp["data"] or []

if not items:
    st.info("Your pantry is empty. Add some items above!")
else:
    st.subheader("Current Items")

    for item in items:
        cols = st.columns([4, 2, 2, 2, 2])
        cols[0].markdown(f"**{item['name']}**")
        cols[1].markdown(item.get("category") or "-")
        cols[2].markdown(f"{item.get('quantity', '')} {item.get('unit', '')}")

        expiry = item.get("expiry_date")
        if expiry:
            cols[3].markdown(f"🕒 {expiry}")
        else:
            cols[3].markdown("—")

        # Delete button
        if cols[4].button("Delete", key=f"delete_{item['id']}"):
            del_resp = delete_pantry_item(token, item["id"])
            if del_resp["code"] >= 400:
                st.error(f"Failed to delete: {del_resp['message']}")
            else:
                st.success(f"Deleted {item['name']} from pantry.")
                st.rerun()