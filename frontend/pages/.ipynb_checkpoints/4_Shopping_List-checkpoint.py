# frontend/pages/4_Shopping_List.py

import streamlit as st
from utils.api import create_shopping_list

st.set_page_config(page_title="Shopping List", page_icon="🛒")

st.title("🛒 Shopping List Helper")

token = st.session_state.get("token")
if not token:
    st.error("Please log in first on the main page.")
    st.stop()

st.write(
    "Paste the recipe name and its ingredients. "
    "AppetIte will compare with your pantry and tell you what to buy."
)

with st.form("shopping_list_form"):
    recipe_name = st.text_input("Recipe name", placeholder="Tomato Pasta")
    ingredients_text = st.text_area(
        "Recipe ingredients (comma separated)",
        placeholder="pasta, tomato, garlic, olive oil, salt",
    )
    submitted = st.form_submit_button("Generate shopping list")

if submitted:
    ingredients = [i.strip() for i in ingredients_text.split(",") if i.strip()]
    if not recipe_name:
        st.warning("Please enter a recipe name.")
    elif not ingredients:
        st.warning("Please enter at least one ingredient.")
    else:
        data, code = create_shopping_list(token, recipe_name, ingredients)
        if code != 200:
            st.error(f"Error creating shopping list: {data}")
        else:
            st.success(f"Shopping list created for **{recipe_name}**.")
            missing = data.get("items", [])
            if not missing:
                st.info("You already have everything in your pantry. No need to buy anything!")
            else:
                st.subheader("You need to buy:")
                for item in missing:
                    st.markdown(f"- {item}")