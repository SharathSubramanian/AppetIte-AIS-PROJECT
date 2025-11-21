# frontend/pages/3_Quick_Generate.py

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.api import quick_generate

st.set_page_config(page_title="Quick Generate", page_icon="⚡", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first from the main page.")
    st.stop()

st.title("⚡ Quick Recipe Generator")
st.write(
    "Type a few ingredients and let AppetIte suggest a recipe "
    "(this ignores your saved pantry)."
)

ingredients_text = st.text_area(
    "Ingredients (comma separated)",
    placeholder="Example: pasta, garlic, olive oil, chilli flakes",
    height=100,
)

if st.button("Generate"):
    raw = ingredients_text.strip()
    if not raw:
        st.error("Please enter at least one ingredient.")
    else:
        ingredients: List[str] = [x.strip() for x in raw.split(",") if x.strip()]

        resp = quick_generate(token, ingredients)

        # Resp is always: {"code": int, "message": str, "data": Any}
        if resp["code"] != 200 or not resp["data"]:
            st.error(
                f"Failed to generate recipe (HTTP {resp['code']}): {resp['message']}"
            )
        else:
            data: Dict[str, Any] = resp["data"]
            recipe: Dict[str, Any] = data.get("recipe", {})

            title = recipe.get("title", "Quick Recipe")
            ing_list = recipe.get("ingredients") or ingredients
            instructions = recipe.get(
                "instructions",
                "No detailed instructions returned. Use the ingredients creatively!",
            )
            category = recipe.get("category") or "Quick & Easy"

            st.subheader(title)
            st.caption(f"Category: {category}")

            st.markdown("**Ingredients:**")
            for ing in ing_list:
                st.markdown(f"- {ing}")

            st.markdown("**Instructions:**")
            st.write(instructions)