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
    st.info("Press 'Get recommendations' to see suggestions based on your pantry.")
    st.stop()

with st.spinner("Fetching recommendations..."):
    resp = get_recommendations(token, category=category_value)

if resp["code"] >= 400:
    st.error(f"Failed to get recommendations: {resp['message']}")
    st.stop()

recipes: List[Dict[str, Any]] = resp["data"] or []

if not recipes:
    st.info("No recipes could be recommended from your current pantry.")
    st.stop()

st.subheader("Suggested recipes")

for idx, recipe in enumerate(recipes):
    with st.container():
        st.markdown(f"### {recipe.get('title', f'Recipe {idx+1}')}")
        cat = recipe.get("category")
        if cat:
            st.caption(f"Category: {cat}")

        ings = recipe.get("ingredients") or []
        st.markdown("**Ingredients:**")
        for ing in ings:
            st.markdown(f"- {ing}")

        st.markdown("**Instructions:**")
        st.write(recipe.get("instructions", "No instructions available."))

        cols = st.columns([1, 1, 2])
        with cols[0]:
            if st.button("Cook this", key=f"cook_{idx}"):
                cook_resp = cook_recipe(
                    token=token,
                    recipe_title=recipe.get("title", f"Recipe {idx+1}"),
                    ingredients=ings,
                )
                if cook_resp["code"] >= 400:
                    st.error(f"Failed to cook recipe: {cook_resp['message']}")
                else:
                    st.success("Pantry updated for this recipe. Enjoy your meal! 🍽️")
                    st.rerun()

        # ✅ feedback for recommend page
        with cols[1]:
            with st.popover("Leave feedback", use_container_width=True):
                rating = st.select_slider(
                    "Rating",
                    options=[1, 2, 3, 4, 5],
                    value=5,
                    key=f"rec_rate_{idx}",
                )
                comment = st.text_area(
                    "Comment (optional)",
                    key=f"rec_comment_{idx}",
                )
                if st.button("Submit", key=f"rec_submit_{idx}"):
                    fb_resp = submit_feedback(
                        token=token,
                        page="recommend",
                        rating=rating,
                        comment=comment.strip() or None,
                    )
                    if fb_resp["code"] >= 400:
                        st.error(f"Feedback failed: {fb_resp['message']}")
                    else:
                        st.success("Thanks! Feedback recorded ✅")