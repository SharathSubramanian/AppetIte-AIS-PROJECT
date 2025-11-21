import streamlit as st

from utils.api import add_pantry, get_pantry, delete_pantry_item


st.set_page_config(page_title="AppetIte Pantry", page_icon="🧺", layout="centered")

# Guard: must be logged in
token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🧺 My Pantry")

st.subheader("Add an item")

with st.form("add_pantry_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Ingredient name")
        category = st.selectbox(
            "Category",
            [
                "vegetable",
                "fruit",
                "grain",
                "protein",
                "dairy",
                "spice",
                "other",
            ],
            index=0,
        )
    with col2:
        quantity = st.number_input("Quantity", min_value=0.0, step=0.5, value=1.0)
        unit = st.text_input("Unit (g, ml, pcs, etc.)", value="pcs")

    expiry_date = st.date_input("Expiry date (optional)", value=None, format="YYYY-MM-DD")
    submitted = st.form_submit_button("Add to pantry")

    if submitted:
        expiry_str = expiry_date.isoformat() if expiry_date else None
        resp = add_pantry(
            token=token,
            name=name.strip(),
            category=category,
            quantity=quantity,
            unit=unit.strip(),
            expiry_date=expiry_str,
        )
        if resp["code"] in (200, 201):
            st.success("Item added to pantry.")
            st.rerun()
        else:
            st.error(f"Failed to add item: {resp['message']}")

st.divider()
st.subheader("Current pantry")

resp = get_pantry(token)
if resp["code"] != 200:
    st.error(f"Could not load pantry: {resp['message']}")
    st.stop()

items = resp["data"] or []

if not items:
    st.info("Your pantry is empty. Add some items above!")
else:
    for item in items:
        cols = st.columns([3, 2, 2, 3, 2])
        with cols[0]:
            st.markdown(f"**{item.get('name', '')}**")
        with cols[1]:
            st.text(item.get("category", ""))
        with cols[2]:
            st.text(f"{item.get('quantity', '')} {item.get('unit', '')}")
        with cols[3]:
            exp = item.get("expiry_date")
            st.text(exp if exp else "—")
        with cols[4]:
            if st.button("Delete", key=f"del-{item.get('id')}"):
                del_resp = delete_pantry_item(token, item.get("id"))
                if del_resp["code"] in (200, 204):
                    st.success("Item deleted.")
                else:
                    st.error(f"Failed to delete item: {del_resp['message']}")
                st.rerun()