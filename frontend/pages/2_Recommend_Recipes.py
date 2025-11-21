# frontend/pages/2_Recommend_Recipes.py

from typing import Any, Dict, List, Optional

import streamlit as st

from utils.api import get_pantry, get_recommendations, cook_recipe

st.set_page_config(page_title="Recommendations", page_icon="🍽️", layout="wide")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🍽️ Recommended Recipes")

st.write("AppetIte suggests recipes based on your pantry items.")

# Optional filter by category
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

        # Cook this button
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