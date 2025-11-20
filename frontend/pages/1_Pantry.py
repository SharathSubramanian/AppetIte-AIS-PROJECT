# frontend/pages/1_Pantry.py

import datetime

import streamlit as st

from utils.api import add_pantry_item, get_pantry

st.title("🍽️ Pantry")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in from the main page first.")
    st.stop()

col_form, col_list = st.columns([1, 2])

with col_form:
    st.subheader("Add item")

    name = st.text_input("Name")
    category = st.selectbox(
        "Category",
        ["vegetable", "fruit", "grain", "protein", "dairy", "spice", "snack", "other"],
    )
    quantity = st.number_input("Quantity", min_value=0.0, value=1.0, step=0.5)
    unit = st.text_input("Unit (e.g. pcs, g, ml)", value="pcs")

    expiry_date_value = st.date_input(
        "Expiry date (optional)",
        value=None,
        min_value=datetime.date.today(),
        format="YYYY-MM-DD",
    )

    if st.button("Add to pantry"):
        expiry_str = (
            expiry_date_value.isoformat() if isinstance(expiry_date_value, datetime.date) else None
        )
        data, code = add_pantry_item(
            token,
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_str,
        )
        if code in (200, 201):
            st.success("Item added to pantry ✅")
            st.rerun()
        else:
            st.error(f"Failed to add item: {data}")

with col_list:
    st.subheader("Current pantry")

    data, code = get_pantry(token)
    if code == 200 and isinstance(data, list):
        if not data:
            st.info("Your pantry is empty. Add something on the left!")
        else:
            # Pretty table
            import pandas as pd  # local import to avoid global dependency issues

            df = pd.DataFrame(data)
            # Show only relevant columns in a nice order if they exist
            columns = [c for c in ["name", "category", "quantity", "unit", "expiry_date", "created_at"] if c in df.columns]
            st.dataframe(df[columns])
    else:
        st.error(f"Could not load pantry: {data}")