from typing import List, Dict, Any

import streamlit as st

from utils.api import get_pantry, create_shopping_list


st.set_page_config(page_title="Shopping List", page_icon="🛒", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🛒 Shopping List Helper")

st.write(
    "Paste or type the ingredients for a recipe and let AppetIte compare "
    "them against your pantry to find what you need to buy."
)

# Load pantry for display
pantry_resp = get_pantry(token)
if pantry_resp["code"] != 200:
    st.error(f"Could not load pantry: {pantry_resp['message']}")
    st.stop()

pantry_items: List[Dict[str, Any]] = pantry_resp["data"] or []

with st.expander("View current pantry"):
    if not pantry_items:
        st.info("Your pantry is empty.")
    else:
        for item in pantry_items:
            st.markdown(
                f"**{item.get('name', '')}** — "
                f"{item.get('quantity', '')} {item.get('unit', '')} "
                f"({item.get('category', '')})"
            )

st.subheader("Recipe ingredients")

recipe_name = st.text_input("Recipe name", value="My Dish")
ingredients_text = st.text_area(
    "List ingredients (one per line or comma separated)",
    placeholder="Example:\n"
    "tomato\n"
    "onion\n"
    "garlic\n"
    "olive oil\n"
    "basil",
)

if st.button("Generate shopping list"):
    raw = ingredients_text.strip()
    if not raw:
        st.error("Please enter at least one ingredient.")
    else:
        # Accept both line and comma separated
        lines = []
        for line in raw.splitlines():
            parts = [p.strip() for p in line.split(",") if p.strip()]
            lines.extend(parts)

        recipe_ingredients: List[str] = lines

        resp = create_shopping_list(token, recipe_name, recipe_ingredients)
        if resp["code"] != 200:
            st.error(f"Could not compute shopping list: {resp['message']}")
        else:
            data = resp["data"] or {}
            missing_items = data.get("items", [])

            st.subheader("Missing ingredients")

            if not missing_items:
                st.success("You already have everything you need in your pantry. 🎉")
            else:
                for item in missing_items:
                    name = item.get("name", "")
                    qty = item.get("quantity", "")
                    unit = item.get("unit", "")
                    st.markdown(f"- **{name}** — {qty} {unit}")