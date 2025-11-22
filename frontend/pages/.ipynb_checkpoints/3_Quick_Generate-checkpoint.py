# frontend/pages/3_Quick_Generate.py
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.api import quick_generate, submit_feedback

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

recipe_shown: Dict[str, Any] | None = None
ings_used: List[str] = []

if st.button("Generate"):
    raw = ingredients_text.strip()
    if not raw:
        st.error("Please enter at least one ingredient.")
    else:
        ings_used = [x.strip() for x in raw.split(",") if x.strip()]

        resp = quick_generate(token, ings_used)

        if resp["code"] != 200 or not resp["data"]:
            st.error(
                f"Failed to generate recipe (HTTP {resp['code']}): {resp['message']}"
            )
        else:
            data: Dict[str, Any] = resp["data"]
            recipe_shown = data.get("recipe", {})

            title = recipe_shown.get("title", "Quick Recipe")
            ing_list = recipe_shown.get("ingredients") or ings_used
            instructions = recipe_shown.get(
                "instructions",
                "No detailed instructions returned. Use the ingredients creatively!",
            )
            category = recipe_shown.get("category") or "Quick & Easy"

            st.subheader(title)
            st.caption(f"Category: {category}")

            st.markdown("**Ingredients:**")
            for ing in ing_list:
                st.markdown(f"- {ing}")

            st.markdown("**Instructions:**")
            st.write(instructions)

            st.divider()

            # ✅ feedback for quickgen
            st.subheader("Give feedback on this recipe")
            rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5)
            comment = st.text_area("Comment (optional)")
            if st.button("Submit feedback"):
                fb_resp = submit_feedback(
                    token=token,
                    page="quickgen",
                    rating=rating,
                    comment=comment.strip() or None,
                )
                if fb_resp["code"] >= 400:
                    st.error(f"Feedback failed: {fb_resp['message']}")
                else:
                    st.success("Thanks! Feedback recorded ✅")