from typing import Any, Dict, List
import streamlit as st

from utils.api import quick_generate, submit_feedback

st.set_page_config(page_title="Quick Generate", page_icon="⚡", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("⚡ Quick Recipe Generator")
st.write("Enter ingredients to instantly generate a recipe.")

ingredients_text = st.text_area(
    "Ingredients (comma separated)",
    placeholder="Example: pasta, garlic, olive oil",
    height=100,
)

if st.button("Generate"):
    raw = ingredients_text.strip()
    if not raw:
        st.error("Enter at least one ingredient.")
    else:
        ingredients = [x.strip() for x in raw.split(",") if x.strip()]

        resp = quick_generate(token, ingredients)
        if resp["code"] != 200:
            st.error(f"Failed (HTTP {resp['code']}): {resp['message']}")
        else:
            recipe = resp["data"]["recipe"]

            st.subheader(recipe.get("title"))
            st.caption(recipe.get("category", "Quick & Easy"))

            st.markdown("**Ingredients:**")
            for ing in recipe.get("ingredients", []):
                st.markdown(f"- {ing}")

            st.markdown("**Instructions:**")
            st.write(recipe.get("instructions"))

            st.divider()

            # ------- FEEDBACK -------
            st.subheader("⭐ Rate this recipe")

            rating = st.radio("Was this helpful?", [1,2,3,4,5], horizontal=True)
            comment = st.text_area("Optional comment")

            if st.button("Submit feedback", key="fb_qg"):
                fb = submit_feedback(token, page="quickgen", rating=rating, comment=comment)
                if fb["code"] == 201:
                    st.success("Thanks! Feedback recorded.")
                else:
                    st.error("Could not submit feedback.")