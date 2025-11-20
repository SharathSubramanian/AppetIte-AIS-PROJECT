# frontend/pages/3_Quick_Generate.py

import streamlit as st
from utils.api import quick_generate

st.set_page_config(page_title="Quick Generate", page_icon="⚡")

st.title("⚡ Quick Recipe Generator")

token = st.session_state.get("token")
if not token:
    st.error("Please log in first on the main page.")
    st.stop()

st.write("Type a few ingredients you have right now and AppetIte will suggest a quick recipe.")

ingredients_text = st.text_input(
    "Ingredients (comma separated)", placeholder="pasta, garlic, olive oil"
)

if st.button("Generate recipe"):
    ingredients = [i.strip() for i in ingredients_text.split(",") if i.strip()]
    if not ingredients:
        st.warning("Please enter at least one ingredient.")
    else:
        data, code = quick_generate(token, ingredients)
        if code != 200:
            st.error(f"Error generating recipe: {data}")
        else:
            recipe = data.get("recipe", {})
            st.markdown(f"### 🍽️ {recipe.get('title', 'Quick recipe')}")
            cat = recipe.get("category")
            if cat:
                label = {
                    "healthy": "Healthy",
                    "cheat_meal": "Cheat meal",
                    "easy_to_cook": "Easy to cook",
                }.get(cat, cat)
                st.caption(f"Category: **{label}**")

            ings = recipe.get("ingredients") or []
            if ings:
                st.markdown("**Ingredients:**")
                st.write(", ".join(ings))

            st.markdown("**Instructions:**")
            st.write(recipe.get("instructions", "No instructions provided."))