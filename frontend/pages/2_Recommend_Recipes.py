# frontend/pages/2_Recommend_Recipes.py

from typing import Any, Dict, List, Optional

import streamlit as st

from utils.api import get_recommendations, cook_recipe, submit_feedback

st.set_page_config(page_title="Recommendations", page_icon="🍽️", layout="wide")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🍽️ Recommended Recipes")
st.write("AppetIte suggests recipes based on your pantry items.")

category = st.selectbox(
    "Filter by category (optional)",
    ["", "healthy", "cheat meal", "easy to cook", "comfort food", "high protein"],
    index=0,
)
category_value: Optional[str] = category or None

if st.button("Get recommendations"):
    st.session_state["recs_triggered"] = True

if not st.session_state.get("recs_triggered"):
    st.info("Press 'Get recommendations' to see suggestions.")
    st.stop()

with st.spinner("Fetching recommendations..."):
    resp = get_recommendations(token, category=category_value)

if resp["code"] >= 400:
    st.error(f"Failed to get recommendations: {resp['message']}")
    st.stop()

recipes: List[Dict[str, Any]] = resp["data"] or []

if not recipes:
    st.info("No recipes match your pantry.")
    st.stop()

st.subheader("Suggested Recipes")

for idx, recipe in enumerate(recipes):
    with st.container():
        st.markdown(f"### {recipe.get('title', f'Recipe {idx+1}')}")
        if recipe.get("category"):
            st.caption(f"Category: {recipe['category']}")

        ings = recipe.get("ingredients", [])
        st.markdown("**Ingredients:**")
        for ing in ings:
            st.markdown(f"- {ing}")

        st.markdown("**Instructions:**")
        st.write(recipe.get("instructions", "No instructions available."))

        if st.button("Cook this", key=f"cook_{idx}"):
            cook_resp = cook_recipe(
                token=token,
                recipe_title=recipe.get("title", f"Recipe {idx+1}"),
                ingredients=ings,
            )
            if cook_resp["code"] >= 400:
                st.error(f"Failed: {cook_resp['message']}")
            else:
                st.success("Pantry updated. Enjoy! 🍽️")
                st.rerun()

        st.divider()

# ---------------- FEEDBACK FORM ----------------

st.subheader("⭐ Rate these recommendations")

rating = st.radio("How useful were these recipes?", [1,2,3,4,5], horizontal=True)
comment = st.text_area("Optional comment")

if st.button("Submit feedback", key="fb_recommend"):
    resp = submit_feedback(token, page="recommend", rating=rating, comment=comment)
    if resp["code"] == 201:
        st.success("Thanks for your feedback!")
    else:
        st.error("Could not submit feedback.")