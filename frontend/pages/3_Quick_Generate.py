# frontend/pages/3_Quick_Generate.py

from typing import List, Dict, Any
import streamlit as st
from utils.api import quick_generate

st.set_page_config(page_title="Quick Generate", page_icon="⚡", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("⚡ Quick Recipe Generator")
st.write("Type a few ingredients and let AppetIte suggest a recipe (ignores pantry).")

ingredients_text = st.text_area(
    "Ingredients (comma separated)",
    placeholder="Example: pasta, garlic, olive oil, chilli flakes",
)

if st.button("Generate"):
    raw = ingredients_text.strip()
    if not raw:
        st.error("Please enter at least one ingredient.")
        st.stop()

    ingredients = [x.strip() for x in raw.split(",") if x.strip()]
    resp = quick_generate(token, ingredients)

    # -------------------------
    # ✔ Correct response format
    # -------------------------
    if resp.get("status") != "success":
        st.error(resp.get("message", "Failed to generate recipe."))
        st.stop()

    data = resp.get("data", {})
    recipe = data.get("recipe", {})

    # -------------------------
    # ✔ Safe extraction
    # -------------------------
    title = recipe.get("title") or "Quick Recipe"
    instructions = recipe.get("instructions") or "No instructions provided."
    category = recipe.get("category") or "quick & easy"
    ing_list = recipe.get("ingredients") or ingredients

    # -------------------------
    # ✔ Render cleanly
    # -------------------------
    st.subheader(title)
    st.caption(f"Category: {category}")

    st.markdown("### Ingredients")
    for ing in ing_list:
        st.markdown(f"- {ing}")

    st.markdown("### Instructions")
    st.write(instructions)