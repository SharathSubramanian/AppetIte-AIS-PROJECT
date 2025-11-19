import streamlit as st
from utils.api import get_pantry, add_pantry_item

st.set_page_config(page_title="Pantry", page_icon="🍽️")

if "token" not in st.session_state or st.session_state.token is None:
    st.error("Please login first.")
    st.stop()

st.title("🍽️ Pantry Inventory")

# Fetch pantry items
pantry, code = get_pantry(st.session_state.token)
if code == 200:
    st.subheader("Your Pantry Items")
    
    if len(pantry) == 0:
        st.info("Your pantry is empty. Add an item!")
    else:
        for item in pantry:
            st.markdown(f"""
                **{item['name'].capitalize()}**  
                Category: {item['category']}  
                Quantity: {item['quantity']} {item['unit']}  
                Expiry: {item['expiry_date']}
                ---
            """)
else:
    st.error("Failed to load pantry.")

# Add new pantry item
st.subheader("Add Item To Pantry")

name = st.text_input("Ingredient")
category = st.text_input("Category")
quantity = st.number_input("Quantity", min_value=0.1)
unit = st.text_input("Unit (e.g. pcs, grams)")
expiry = st.date_input("Expiry Date (optional)", value=None)

if st.button("Add Item"):
    item = {
        "name": name,
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "expiry_date": str(expiry) if expiry else None
    }
    data, code = add_pantry_item(st.session_state.token, item)
    if code in (200, 201):
        st.success("Added!")
        st.experimental_rerun()
    else:
        st.error("Failed to add item.")