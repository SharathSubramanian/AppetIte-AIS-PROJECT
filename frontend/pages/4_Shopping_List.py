import streamlit as st
from utils.api import create_shopping_list

st.title("🛒 Shopping List Generator")

recipe_name = st.text_input("Recipe Name")
ingredients = st.text_area("Recipe Ingredients (comma-separated)")

if st.button("Generate Shopping List"):
    ing_list = [i.strip() for i in ingredients.split(",") if i.strip()]
    data, code = create_shopping_list(st.session_state.token, recipe_name, ing_list)
    if code == 200:
        st.success("Shopping list created!")
        st.write("### Missing Ingredients:")
        st.write(data["items"])
    else:
        st.error("Failed to create list.")