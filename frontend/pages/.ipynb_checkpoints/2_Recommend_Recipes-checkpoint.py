from typing import List, Dict, Any

import streamlit as st

from utils.api import get_pantry, get_recommendations, delete_pantry_item


st.set_page_config(page_title="AppetIte Recommendations", page_icon="🍽️", layout="centered")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🍽️ Recommended Recipes from Your Pantry")

# Load pantry once
pantry_resp = get_pantry(token)
if pantry_resp["code"] != 200:
    st.error(f"Could not load pantry: {pantry_resp['message']}")
    st.stop()

pantry_items: List[Dict[str, Any]] = pantry_resp["data"] or []

category = st.selectbox(
    "Choose a style",
    [
        "Any",
        "Healthy",
        "Quick & Easy",
        "Comfort / Cheat Meal",
        "High Protein",
        "Budget Friendly",
    ],
    index=0,
)

if st.button("Get recipes"):
    st.session_state["recommend_category"] = category

selected_category = st.session_state.get("recommend_category", "Any")

if "recommend_category" not in st.session_state:
    st.info("Choose a style and click **Get recipes** to see suggestions.")
    st.stop()

st.write(f"Showing recipes for: **{selected_category}**")

rec_resp = get_recommendations(token, selected_category)
if rec_resp["code"] != 200:
    st.error(f"Failed to get recipes: {rec_resp['message']}")
    st.stop()

recipes: List[Dict[str, Any]] = rec_resp["data"] or []


def _clean_title(title: str) -> str:
    title = (title or "Untitled Recipe").strip()
    if not title:
        return "Untitled Recipe"
    # Capitalize nicely
    return title[0].upper() + title[1:]


# Deduplicate by title (case-insensitive)
seen = set()
unique_recipes: List[Dict[str, Any]] = []
for r in recipes:
    t = _clean_title(r.get("title", "Untitled Recipe"))
    key = t.lower()
    if key in seen:
        continue
    seen.add(key)
    r["title"] = t
    unique_recipes.append(r)

recipes = unique_recipes


def _match_pantry_for_recipe(recipe: Dict[str, Any], pantry: List[Dict[str, Any]]) -> List[int]:
    """
    Very simple matching:
    - Lowercase ingredient strings
    - Lowercase pantry item names
    - If ingredient and item name overlap (substring), we treat it as "used".
    Returns list of pantry item IDs to delete.
    """
    ingredient_names = [str(x).lower() for x in recipe.get("ingredients", [])]
    matched_ids = set()

    for item in pantry:
        item_name = str(item.get("name", "")).lower()
        item_id = item.get("id")
        if not item_id:
            continue
        for ing in ingredient_names:
            if item_name and (item_name in ing or ing in item_name):
                matched_ids.add(item_id)
                break

    return list(matched_ids)


if not recipes:
    st.info("No recipes found from your pantry yet. Try adding more items.")
else:
    st.subheader("Suggestions")

    for idx, recipe in enumerate(recipes):
        title = _clean_title(recipe.get("title", "Untitled Recipe"))
        category_tag = recipe.get("category") or selected_category
        ingredients = recipe.get("ingredients", [])
        instructions = recipe.get("instructions", "")

        with st.expander(f"{title}  —  *{category_tag}*"):
            st.markdown("**Ingredients:**")
            if ingredients:
                for ing in ingredients:
                    st.markdown(f"- {ing}")
            else:
                st.write("No ingredient list available.")

            st.markdown("**Instructions:**")
            st.write(instructions or "No instructions provided.")

            if st.button("🍳 Cook this", key=f"cook-{idx}"):
                used_ids = _match_pantry_for_recipe(recipe, pantry_items)
                if not used_ids:
                    st.warning("None of your pantry items matched this recipe's ingredients.")
                else:
                    failed = False
                    for pid in used_ids:
                        del_resp = delete_pantry_item(token, pid)
                        if del_resp["code"] not in (200, 204):
                            failed = True
                    if failed:
                        st.error("Some items could not be removed from pantry.")
                    else:
                        st.success("Pantry updated for this recipe. Happy cooking! 🍳")
                    st.rerun()