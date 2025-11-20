# frontend/pages/2_Recommend_Recipes.py

from typing import List

import streamlit as st

from utils.api import (
    create_shopping_list,
    cook_recipe,
    get_pantry,
    get_recommendations,
)

st.title("🧠 Recommended Recipes")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in from the main page first.")
    st.stop()

st.write(
    "These recipes are generated from your current pantry. "
    "Pick a category to nudge the style of the recipe."
)

CATEGORY_OPTIONS = {
    "Any": None,
    "Healthy": "healthy",
    "Cheat meal": "cheat meal",
    "Easy to cook": "easy to cook",
    "Comfort food": "comfort food",
    "High protein": "high protein",
}

col_cat, col_btn = st.columns([2, 1])

with col_cat:
    category_label = st.selectbox("Filter by category", list(CATEGORY_OPTIONS.keys()))
    selected_category = CATEGORY_OPTIONS[category_label]

with col_btn:
    if st.button("🔍 Get recommendations"):
        data, code = get_recommendations(token, category=selected_category)
        if code == 200 and isinstance(data, list):
            st.session_state["recommended_recipes"] = data
        else:
            st.error(f"Could not fetch recommendations: {data}")

recipes: List[dict] = st.session_state.get("recommended_recipes", [])

if not recipes:
    st.info("No recipes yet — click **Get recommendations** to generate some.")
    st.stop()

st.subheader("Suggestions based on your pantry")

for idx, recipe in enumerate(recipes):
    title = recipe.get("title", f"Recipe {idx+1}")
    category = recipe.get("category")
    ingredients = recipe.get("ingredients", [])
    instructions = recipe.get("instructions", "")

    header = title
    if category:
        header += f"  •  _{category}_"

    with st.expander(header, expanded=False):
        st.markdown("**Ingredients**")
        if ingredients:
            for ing in ingredients:
                st.write(f"- {ing}")
        else:
            st.write("No ingredient list provided.")

        st.markdown("**Instructions**")
        st.write(instructions or "No instructions provided.")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("🛒 Create shopping list", key=f"shop_{idx}"):
                data, code = create_shopping_list(
                    token,
                    recipe_name=title,
                    recipe_ingredients=ingredients,
                )
                if code in (200, 201):
                    missing = data.get("items", [])
                    if missing:
                        st.success(
                            "Shopping list created. You need to buy:\n"
                            + ", ".join(missing)
                        )
                    else:
                        st.success(
                            "You already have everything in your pantry for this recipe! 🎉"
                        )
                else:
                    st.error(f"Failed to create shopping list: {data}")

        with c2:
            if st.button("🍳 Cook!", key=f"cook_{idx}"):
                data, code = cook_recipe(
                    token,
                    recipe_name=title,
                    recipe_ingredients=ingredients,
                )
                if code == 200:
                    st.success("Marked as cooked. Pantry has been updated.")
                    # Optional: refresh pantry in the background; user can see it on Pantry tab.
                else:
                    st.error(f"Failed to cook recipe: {data}")